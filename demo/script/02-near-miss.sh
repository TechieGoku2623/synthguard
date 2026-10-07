#!/usr/bin/env bash
set +e
synthguard screen --fasta data/sample/near-miss.fa --explain --summary
exit $?
