#!/bin/bash

echo "job running in host: "
echo `hostname`
echo "job starting"
/usr/lib/compucell3d/runScript.sh -i /srv/home/jarias/mxan_indirect_csg/mxan_indirect_csg.cc3d -f 50
echo "job ended"
