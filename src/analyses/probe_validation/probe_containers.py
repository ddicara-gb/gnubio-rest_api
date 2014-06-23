from collections import namedtuple

from Bio import SeqIO, SearchIO
import os
import subprocess
from uuid import uuid4
from Bio.Seq import Seq, reverse_complement
from Bio.SeqRecord import SeqRecord

from src.analyses.probe_validation import settings
from src.analyses.probe_validation.ncbi_util import chromosome_for_ref_assembly
from src.analyses.probe_validation.probe_util import get_tm_checker

__author__ = 'spowers'


def _find_amplicon_in_refgenome(amplicon):
    #run the search
    filename = str(uuid4())
    SeqIO.write(amplicon, filename + '.fa', 'fasta')
    try:
        _ = subprocess.check_call([settings.blat_location, settings.ref_genome_loc, filename + '.fa', filename + '.psl'])
        search_results = SearchIO.read(filename + '.psl', 'blat-psl')
    except (subprocess.CalledProcessError, ValueError):
        search_results = None
    try:
        os.remove(filename + '.fa')
        os.remove(filename + '.psl')
    except os.OSError:
        return None
    return search_results[0]


class Amplicon(Seq):
    """Amplicon is a type of sequence object which can find its location within the reference genome and store that
    data.  Additional information like mutation locations can also be saved.
    """
    mutation_locations = list()

    def __init__(self, seq_string):
        super(Amplicon, self).__init__(seq_string)
        self.locus = None
        self.position = None
        self.hits = 0

    def find_in_reference(self):
        """utilize an external search util (BLAT or BLAST) to find in the reference genome.  This can then be used to
        find the actual position in the genome for probes later on."""
        if self.locus is None:
            hit = _find_amplicon_in_refgenome(SeqRecord(self))
            self.hits = len(hit)
            if len(hit):
                self.locus = chromosome_for_ref_assembly(hit[0].hit_id)
                self.position = hit[0].hit_start

    def add_ref(self, ref_info):
        self.locus = ref_info['chromosome']
        self.position = ref_info['ref_start']

    def findall(self, probe):
        def search(probe):
            l = list()
            current = self.find(probe)
            while current != -1:
                l.append(current)
                current = self.find(probe, current + 1)
            return l
        locations = search(probe)
        p = reverse_complement(probe)
        locations.extend(search(p))
        return locations

    def relative_to_genomic(self, locations):
        """take a list of locations relative to this amplicon (like for a probe match) and map that to the
        genomic reference locations"""
        self.find_in_reference()
        return map(lambda x: (self.locus, self.position + x), locations)


class ProbeSet(object):
    """ A set of forward and reverse probes for a given sequence.
    """

    def __init__(self, sequence, forward, reverse, f_max=None, r_max=None, f_min=None, r_min=None):
        self.sequence = sequence
        self.forward = forward
        self.reverse = reverse
        self.f_max = f_max
        self.r_max = r_max
        self.f_min = f_min
        self.r_min = r_min

    def aggregate(self):
        """
        :return:a list of all probes within the probeset.
        """
        return list(self.forward) + list(self.reverse)

    def sort(self, util_fn):
        """ Sorts the forward and reverse probes based on their utility score.  Lower score is better utility.
        :param util_fn: a callable scoring function closure.
        :return: None
        """
        self.forward = sorted(self.forward, key=util_fn, reverse=False)
        self.reverse = sorted(self.reverse, key=util_fn, reverse=False)

    def aligned_string(self):
        """
        :return: A tuple of strings with the forward and reverse sequences and their aligned probes below them.  All are
        5' to 3' ordering.
        """
        forward_alignment = [self.sequence.seq.tostring()]
        reverse_alignment = [self.sequence.seq.reverse_complement().tostring()]
        for probe in self.forward:
            location = self.sequence.seq.find(probe)
            forward_alignment.append(' ' * location + probe)
        rc = self.sequence.seq.reverse_complement()
        for probe in self.reverse:
            location = rc.find(probe)
            reverse_alignment.append(' ' * location + probe)
        return '\n'.join(forward_alignment), '\n'.join(reverse_alignment)

    def max_start(self):
        """
        Determine the start location for the probe closest to the 3' end of the amplicon as well as the same for the
        reverse complement sequence.
        :return: A tuple with values for forward and reverse max location.
        """
        if not self.f_max or not self.r_max:
            f = self.sequence.seq.find
            r = map(f, self.forward)
            self.f_max = reduce(max, r, 0)
            f = self.sequence.seq.reverse_complement().find
            r = map(f, self.reverse)
            self.r_max = reduce(max, r, 0)
        return self.f_max, self.r_max

    def min_start(self):
        """
        Determine the minimum start location for probes.  This is needed to determine if the probes are for a large indel
        event.
        :return: A tuple with forward and reverse min locations.
        """

        if not self.f_min or not self.r_min:
            f = self.sequence.seq.find
            r = map(f, self.forward)
            self.f_min = reduce(min, r, float('inf'))
            f = self.sequence.seq.reverse_complement().find
            r = map(f, self.reverse)
            self.r_min = reduce(min, r, float('inf'))
        return self.f_min, self.r_min

    def filter_probes(self, max_position=-6):
        """
        Remove probes from consideration that contain the mutation beyond some allowable limit.
        :param max_position: The maximum position from the 3' end that the mutation should be in.
        :return: None
        """
        tm = get_tm_checker()
        f_m, r_m = self.max_start()
        if self.is_large_indel():
            print self.sequence.name
            self._filter_for_indel()
        else:
            self.forward = filter(lambda x: self.sequence.seq.find(x) + len(x) + max_position <= f_m, self.forward)
            self.forward = filter(lambda x: tm(x) is not None, self.forward)
            rc = self.sequence.seq.reverse_complement()
            self.reverse = filter(lambda x: rc.find(x) + len(x) + max_position <= r_m, self.reverse)
            self.reverse = filter(lambda x: tm(x) is not None, self.reverse)

    def is_large_indel(self, threshold=30):
        """
        :return: True if the probes are associated with a large indel event.
        """
        f_min, r_min = self.min_start()
        f_max, r_max = self.max_start()
        if f_max - f_min >= threshold or r_max - r_min >= threshold:
            return True
        else:
            return False

    def _filter_for_indel(self, exclusion_distance=35):
        """
        Remove probes too close to the 5' location for large indels where the probes will be all over the target sequence.
        :return: None
        """
        f_m, r_m = self.max_start()
        self.forward = filter(lambda x: self.sequence.seq.find(x) >= f_m - exclusion_distance, self.forward)
        rc = self.sequence.seq.reverse_complement().find
        self.reverse = filter(lambda x: rc(x) >= r_m - exclusion_distance, self.reverse)

    def __eq__(self, other):
        if self.sequence.seq.tostring() == other.sequence.seq.tostring() and self.forward == other.forward and self.reverse == other.reverse:
            return True
        else:
            return False


class AmpliconSet(namedtuple('AmpliconSet', 'name wildtype mutants')):
    """ A container for the probesets related to a give target amplicon.
    """

    def aggregate(self):
        """
        Aggregate all of the probes in this amplicon set.
        :return:
        """
        results = self.wildtype.aggregate()
        for m in self.mutants:
            results.extend(m.aggregate())
        return results

