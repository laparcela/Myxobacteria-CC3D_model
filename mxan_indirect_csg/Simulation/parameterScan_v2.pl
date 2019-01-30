#!/usr/bin/perl

#################################################################################################################################
# This file contains a set of subroutines (which work consequtively and are intented to be useful to perform parameter scanning over CC3D models. Though CC3D plattform offers a parameter scan function this script is aimed to got easier through the process.
#
# Dependencies: 
# - Perl v5.24.0 
# - CC3D v3.7.5.
#
# Developed by: Juan Antonio Arias Del Angel (PhD student) - Universidad Nacional Autónoma de Mexico - Instituto de Ecología
# Contact: jariasdelangel@gmail.com
# Advisor: Mariana Benitez Keinrad (PhD) - Universidad Nacional Autónoma de Mexico - Instituto de Ecología
# Contact: marianabk@gmail.com 
#
# This script was develop as part of a researched project aimed to understand the spatial dynamic of cell fate determination during the fruiting body formation in Myxococcus xanthus development. This project is part of the PhD thesis developed by Juan Antonio Arias Del Angel  
# 
# Last modification: Nov-09-2017
#
# Reference to CC3D software: Swat, M. H., Thomas, G. L., Belmonte, J. M., Shirinifard, A., Hmeljak, D., & Glazier, J. A. (2012). Multi-scale modeling of tissues using CompuCell3D. Methods in cell biology, 110, 325.
#
# CC3D website: http://www.compucell3d.org/
#
# WARNING: This script has been only tested over MacOS Yosemite v10.10.5 using CC3D v3.7.5.
#################################################################################################################################


#perl parameterScan_v2.pl -m /Users/ewiggin/Dropbox/Proyectos/CC3D_models/mxan_indirect_csg -s /Users/ewiggin/CC3D_3.7.5/ -p /Users/ewiggin/Dropbox/Proyectos/CC3D_models/mxan_indirect_csg/Simulation/ParametersToScan.txt -c diffA,diffC -n 1
# -m  --model
# -s  --software
# -p  --toScan
# -c  --combinations
# -n  --numSimulations
# Además los argumentos a pasar a runScript.sh

use strict;
use Getopt::Long;


my $path_to_cc3d;
my $path_to_cc3d_software;
my $to_scan;
my $combs;
my $rep;

my @files = ('mxan_indirect_csg.xml', 'mxan_indirect_csg.py', 'mxan_indirect_csgSteppables.py');

GetOptions ("m=s"   => \$path_to_cc3d,    # numeric
            "s=s"   => \$path_to_cc3d_software,      # string
            "p=s"   => \$to_scan,
            "c=s"   => \$combs,
            "n=i"   => \$rep)
or die("Error in command line arguments\n");

print "$path_to_cc3d\n";
print "$path_to_cc3d_software\n";
print "$to_scan\n";
print "$combs\n";
print "$rep\n";


my %parms_values = ();
my %parms_files;

my $parm  = ();
my $value = ();
my @values = ();
my $file  = ();

open(parms, $to_scan);

while(<parms>){
    if(/(.+) (.+) (.+)/){
        $parm  = $1;
        $value = $2;
        $file  = $3;
        
        @values = split(',', $value);
        
        $parms_values{$parm} = [@values];
        $parms_files{$parm}  = $file;
        
        
    }
    
} close(parms);

foreach $parm (keys(%parms_values)){
    print "$parm\t@{$parms_values{$parm}}\t$parms_files{$parm}\n";
}

my @combinations = split(':', $combs);
my $number_of_combs = scalar(@combinations);

print "@combinations\n";

print "Performing parameter scan for $number_of_combs combinations of parameters\n";

for(my $c = 0; $c < scalar(@combinations); $c++){
    &parameter_scan($combinations[$c], 0, "", "")
    
}







########################################################################################################
#########################################     Sub-routines     #########################################
########################################################################################################

# Input
# parameters_to_test: parm1,parm2,parm3
# position. Por default 0
# parameters ""
# values 00

sub parameter_scan{
    my $parameters_to_test = $_[0];
    my $pos = $_[1];
    my $parameters = $_[2];
    my $values = $_[3];
    
    my @parameters = split(',', $parameters_to_test);
    print "hola $parms_values{$parameters[$pos]}\n";
    for(my $value = 0; $value < scalar(@{$parms_values{$parameters[$pos]}}); $value++){
        if($pos <= (scalar(@parameters) - 2)){
            &parameter_scan($parameters_to_test, $pos + 1, $parameters . $parameters[$pos] . "-", $values . "${$parms_values{$parameters[$pos]}}[$value]" . "-");
        }
        else{
            my $params = $parameters . $parameters[$pos];
            my $val = $values . "${$parms_values{$parameters[$pos]}}[$value]";
            &modify_files($params, $val);
            

        }
        
    }
}

########################################################################################################


# Input:
# a) $params_to_scan is a character string containing the names of the parameters to scan in the format:
# "param1-param2-param3" as returned by the sub-routine "parameter_scan".
# b) $values_to_scan is a character string containing the values of the paramters to scan in the format:
# "value1-value2-value" as returned by the sub-routine "parameter_scan". Where value1 is the assigned to the param1 and so on.
# In addition the sub-routine uses the global variables "$path_to_cc3d" and "%parms_files".

sub modify_files{
    my $params_to_scan = $_[0];
    my $values_to_scan = $_[1];
    
    my @params_to_scan = split('-', $params_to_scan);
    my @values_to_scan = split('-', $values_to_scan);
    
    my $path_to_cc3d_copy = $path_to_cc3d . '_temp';
    system("cp -r $path_to_cc3d\/ $path_to_cc3d_copy\/");
    
    for(my $p = 0; $p < scalar(@params_to_scan); $p++){
        for(my $f = 0; $f < scalar(@files); $f++){
            my $path_to_file = $path_to_cc3d_copy . "/Simulation/" . $files[$f];
            print "$path_to_file\n";
            print "$path_to_file\n";
            if($path_to_file =~ /.py/){
                if($path_to_file =~ /Steppables.py/){
                    my $from = "\(.*= )[0-9]*[\.\|e+\|e-]*[0-9]*\(.*\)### ParameterScan:$params_to_scan[$p]";
                    my $to   = "\\1$values_to_scan[$p]\\2### ParameterScan:$params_to_scan[$p]";

                    system("sed -i '' -E 's/$from/$to/g' $path_to_file");

                } else {
                    my $from = "\(.*\"\)[0-9]*[\.\|e+\|e-]*[0-9]*\(\".*\)### ParameterScan:$params_to_scan[$p]\|\(.*frequency=\)[0-9]*\(.*\)### ParameterScan:$params_to_scan[$p]";
                    my $to   = "\\1\\3$values_to_scan[$p]\\2\\4### ParameterScan:$params_to_scan[$p]";

                    system("sed -i '' -E 's/$from/$to/g' $path_to_file");
                }
            }
            if($path_to_file =~ /.xml/){
                  my $from = "\(.*>)[0-9]*[\.\|e+\|e-]*[0-9]*\(<.*\)<!-- ParameterScan:$params_to_scan[$p] -->";
                  my $to   = "\\1$values_to_scan[$p]\\2<!-- ParameterScan:$params_to_scan[$p] -->";

                  system("sed -i '' -E 's/$from/$to/g' $path_to_file");
            }
        }
    }
    
    my $path_to_file = $path_to_cc3d_copy . "/Simulation/" . "mxan_indirect_csgSteppables.py";
    my $from = "\(.*### Parameters:\)\(.*)";
    my $to   = "\\1$params_to_scan $values_to_scan\\2";
    system("sed -i '' -E 's/$from/$to/g' $path_to_file");
    &run_simulation($path_to_cc3d_copy);
    
    
    system("rm -r $path_to_cc3d_copy");
    
}

########################################################################################################

# Input:
# directory: a character string specifying the absolute path to the directory where the *.cc3d file is stored.
# In addition the sub-routine also uses the global variable "$rep" to indicate the number of repetions to perform.

sub run_simulation{
    my $directory = $_[0];
    my $repetitions = $rep;
   
    for(my $r = 0; $r < $repetitions; $r++){
        my $command = $path_to_cc3d_software . "runScript.command -i " . $directory . "\/\*\.cc3d" . " --noOutput" . " -f 10000";
        print "$command\n";
        system("$command");
        system("rm -r /Users/ewiggin/Documents/mxan_indirect_csg*")
    }
}