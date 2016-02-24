#!/usr/bin/env python

"""
# =============================================================================

Copyright Government of Canada 2015

Written by: Eric Marinier, Public Health Agency of Canada,
    National Microbiology Laboratory

Funded by the National Micriobiology Laboratory and the Genome Canada / Alberta
    Innovates Bio Solutions project "Listeria Detection and Surveillance
    using Next Generation Genomics"

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

# =============================================================================
"""

import drmaa
import os
import sys
import StringIO
import shutil

from TestingUtility import *
prepareSystemPath()

from neptune.Execution import *

import unittest

class DefaultArgs():

        kmer = 5
        rate = 0.01
        inhits = 1
        exhits = 2
        gap = 5
        size = 5
        gcContent = 0.5
        filterLength = 0.5
        filterPercent = 0.5
        confidence = 0.95
        parallelization = 0
        inclusion = [getPath("tests/data/simple.fasta")]
        exclusion = [getPath("tests/data/alternative.fasta")]
        referenceSize = 12
        reference = ["tests/data/simple.fasta"]
        output = getPath("tests/output/temp.dir")
        seedSize = 11

        defaultSpecification = None
        countSpecification = None
        aggregateSpecification = None
        extractSpecification = None
        databaseSpecification = None
        filterSpecification = None
        consolidateSpecification = None

class TestExecutionConstructor(unittest.TestCase):

    def test_simple(self):

        args = DefaultArgs()

        with drmaa.Session() as session:
            execution = Execution(session, args)

    def test_no_inclusion(self):

        args = DefaultArgs()
        args.inclusion = None

        with drmaa.Session() as session:
            with self.assertRaises(RuntimeError):
                execution = Execution(session, args)

    def test_no_exclusion(self):

        args = DefaultArgs()
        args.exclusion = None

        with drmaa.Session() as session:
            with self.assertRaises(RuntimeError):
                execution = Execution(session, args)

    def test_no_output(self):

        args = DefaultArgs()
        args.output = None

        with drmaa.Session() as session:
            with self.assertRaises(RuntimeError):
                execution = Execution(session, args)

    def test_default_specification(self):

        args = DefaultArgs()
        defaultSpecification = "-l h_vmem=2G -pe smp 1"
        args.defaultSpecification = defaultSpecification

        with drmaa.Session() as session:
            execution = Execution(session, args)

            self.assertEquals(execution.jobManager.countSpecification, defaultSpecification)
            self.assertEquals(execution.jobManager.aggregateSpecification, defaultSpecification)
            self.assertEquals(execution.jobManager.extractSpecification, defaultSpecification)
            self.assertEquals(execution.jobManager.databaseSpecification, defaultSpecification)
            self.assertEquals(execution.jobManager.filterSpecification, defaultSpecification)

    def test_count_specification(self):

        args = DefaultArgs()
        countSpecification = "-l h_vmem=2G -pe smp 1"
        args.countSpecification = countSpecification

        with drmaa.Session() as session:
            execution = Execution(session, args)

            self.assertEquals(execution.jobManager.countSpecification, countSpecification)
            self.assertEquals(execution.jobManager.aggregateSpecification, None)
            self.assertEquals(execution.jobManager.extractSpecification, None)
            self.assertEquals(execution.jobManager.databaseSpecification, None)
            self.assertEquals(execution.jobManager.filterSpecification, None)

    def test_aggregate_specification(self):

        args = DefaultArgs()
        aggregateSpecification = "-l h_vmem=2G -pe smp 1"
        args.aggregateSpecification = aggregateSpecification

        with drmaa.Session() as session:
            execution = Execution(session, args)

            self.assertEquals(execution.jobManager.countSpecification, None)
            self.assertEquals(execution.jobManager.aggregateSpecification, aggregateSpecification)
            self.assertEquals(execution.jobManager.extractSpecification, None)
            self.assertEquals(execution.jobManager.databaseSpecification, None)
            self.assertEquals(execution.jobManager.filterSpecification, None)

    def test_extract_specification(self):

        args = DefaultArgs()
        extractSpecification = "-l h_vmem=2G -pe smp 1"
        args.extractSpecification = extractSpecification

        with drmaa.Session() as session:
            execution = Execution(session, args)

            self.assertEquals(execution.jobManager.countSpecification, None)
            self.assertEquals(execution.jobManager.aggregateSpecification, None)
            self.assertEquals(execution.jobManager.extractSpecification, extractSpecification)
            self.assertEquals(execution.jobManager.databaseSpecification, None)
            self.assertEquals(execution.jobManager.filterSpecification, None)

    def test_database_specification(self):

        args = DefaultArgs()
        databaseSpecification = "-l h_vmem=2G -pe smp 1"
        args.databaseSpecification = databaseSpecification

        with drmaa.Session() as session:
            execution = Execution(session, args)

            self.assertEquals(execution.jobManager.countSpecification, None)
            self.assertEquals(execution.jobManager.aggregateSpecification, None)
            self.assertEquals(execution.jobManager.extractSpecification, None)
            self.assertEquals(execution.jobManager.databaseSpecification, databaseSpecification)
            self.assertEquals(execution.jobManager.filterSpecification, None)

    def test_filter_specification(self):

        args = DefaultArgs()
        filterSpecification = "-l h_vmem=2G -pe smp 1"
        args.filterSpecification = filterSpecification

        with drmaa.Session() as session:
            execution = Execution(session, args)

            self.assertEquals(execution.jobManager.countSpecification, None)
            self.assertEquals(execution.jobManager.aggregateSpecification, None)
            self.assertEquals(execution.jobManager.extractSpecification, None)
            self.assertEquals(execution.jobManager.databaseSpecification, None)
            self.assertEquals(execution.jobManager.filterSpecification, filterSpecification)

""" 
# =============================================================================

CALCULATE EXPECTED K-MER HITS

# =============================================================================
"""
class CalculateExpectedKMerHits(unittest.TestCase):

    """ 
    # =============================================================================

    test_simple

    PURPOSE:
        Tests a simple use case.

    INPUT:
        DEFAULT ARGS:
        gc-content = 0.50
        length = 10000
        k-mer size = 11

    EXPECTED:
        expected = 11.8959

        ((w -k + 1) choose (2)) * (2* ((1 - L) / 2)^2 + 2 * (L / 2)^2)^k 

    # =============================================================================
    """
    def test_simple(self):

        result = Execution.calculateExpectedKMerHits(0.50, 10000, 11)
        expected = 11.8959

        self.assertAlmostEqual(result, expected, 4)

    """ 
    # =============================================================================

    test_low_gc

    PURPOSE:
        Tests when the GC-content is low.

    INPUT:
        DEFAULT ARGS:
        gc-content = 0.01
        length = 10000
        k-mer size = 11

    EXPECTED:
        expected = 19551.9

        ((w -k + 1) choose (2)) * (2* ((1 - L) / 2)^2 + 2 * (L / 2)^2)^k 

    # =============================================================================
    """
    def test_low_gc(self):

        result = Execution.calculateExpectedKMerHits(0.01, 10000, 11)
        expected = 19551.9

        self.assertAlmostEqual(result, expected, 1)

    """ 
    # =============================================================================

    test_high_gc

    PURPOSE:
        Tests when the GC-content is high.

    INPUT:
        DEFAULT ARGS:
        gc-content = 0.99
        length = 10000
        k-mer size = 11

    EXPECTED:
        expected = 19551.9

        ((w -k + 1) choose (2)) * (2* ((1 - L) / 2)^2 + 2 * (L / 2)^2)^k 

    # =============================================================================
    """
    def test_high_gc(self):

        result = Execution.calculateExpectedKMerHits(0.99, 10000, 11)
        expected = 19551.9

        self.assertAlmostEqual(result, expected, 1)

    """ 
    # =============================================================================

    test_short_genome_length

    PURPOSE:
        Tests when the genome size is short.

    INPUT:
        DEFAULT ARGS:
        gc-content = 0.50
        length = 12
        k-mer size = 11

    EXPECTED:
        expected = 0.000000238419

        ((w -k + 1) choose (2)) * (2* ((1 - L) / 2)^2 + 2 * (L / 2)^2)^k 

    # =============================================================================
    """
    def test_short_genome_length(self):

        result = Execution.calculateExpectedKMerHits(0.50, 12, 11)
        expected = 0.000000238419

        self.assertAlmostEqual(result, expected, 12)

    """ 
    # =============================================================================

    test_long_genome_length

    PURPOSE:
        Tests when the genome size is long.

    INPUT:
        DEFAULT ARGS:
        gc-content = 0.50
        length = 1000000000
        k-mer size = 11

    EXPECTED:
        expected = 119209000000

        ((w -k + 1) choose (2)) * (2* ((1 - L) / 2)^2 + 2 * (L / 2)^2)^k 

    # =============================================================================
    """
    def test_long_genome_length(self):

        result = Execution.calculateExpectedKMerHits(0.50, 1000000000, 11)
        expected = 119209287047.3861825466

        self.assertAlmostEqual(result / math.pow(10, 10), expected / math.pow(10, 10), 4)

    """ 
    # =============================================================================

    test_small_kmer_size

    PURPOSE:
        Tests when the k-mer size is small.

    INPUT:
        DEFAULT ARGS:
        gc-content = 0.50
        length = 10000
        k-mer size = 2

    EXPECTED:
        expected = 3124060

        ((w -k + 1) choose (2)) * (2* ((1 - L) / 2)^2 + 2 * (L / 2)^2)^k 

    # =============================================================================
    """
    def test_small_kmer_size(self):

        result = Execution.calculateExpectedKMerHits(0.50, 10000, 2)
        expected = 3124062.6

        self.assertAlmostEqual(result, expected, 1)

    """ 
    # =============================================================================

    test_large_kmer_size

    PURPOSE:
        Tests when the k-mer size is large.

    INPUT:
        DEFAULT ARGS:
        gc-content = 0.50
        length = 10000
        k-mer size = 101

    EXPECTED:
        expected = 0

        ((w -k + 1) choose (2)) * (2* ((1 - L) / 2)^2 + 2 * (L / 2)^2)^k 

    # =============================================================================
    """
    def test_large_kmer_size(self):

        result = Execution.calculateExpectedKMerHits(0.50, 10000, 101)
        expected = 0

        self.assertAlmostEqual(result, expected, 2)

""" 
# =============================================================================

ESTIMATE K-MER SIZE

# =============================================================================
"""
class EstimateKMerSize(unittest.TestCase):

    """ 
    # =============================================================================

    test_simple

    PURPOSE:
        Tests a simple use case.

    INPUT:
        DEFAULT ARGS:
        GC = 0.50
        length = 12

    EXPECTED:
        k = 3

    # =============================================================================
    """
    def test_simple(self):

        args = DefaultArgs()
        args.inclusion = [getPath("tests/data/simple.fasta")]

        with drmaa.Session() as session:
            execution = Execution(session, args)

            execution.estimateKMerSize()

if __name__ == '__main__':
    
    unittest.main()