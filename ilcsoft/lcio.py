##################################################
#
# LCIO module
#
# Author: Jan Engels, DESY
# Date: Jan, 2007
#
##################################################
                                                                                                                                                            
# custom imports
from baseilc import BaseILC
from util import *


class LCIO(BaseILC):
    """ Responsible for the LCIO software installation process. """
    
    def __init__(self, userInput):
        BaseILC.__init__(self, userInput, "LCIO", "lcio")
        
        self.reqfiles = [ ["lib/liblcio.a", "lib/liblcio.so", "lib/liblcio.dylib"] ]
        
        # java required
        self.reqmodules_external = [ "Java" ]
        
        # optional modules
        #self.optmodules = [ "dcap", "ROOT" ]
        self.optmodules = [ "CLHEP", "ROOT" ]

        # flag for using cmake to build LCIO
        self.useCMake = True

        # flag for building lcio java stuff
        self.buildJava = True
        
        # build documentation flag for ant
        self.buildDoc = True

        # flag for building lcio fortran stuff for ant
        self.buildFortran = False

        # supported download types
        self.download.supportedTypes = ["svn"]

        ## set some cvs variables
        ## export CVSROOT=:pserver:anonymous@cvs.freehep.org:/cvs/lcio
        #self.download.accessmode = "pserver"
        #self.download.server = "cvs.freehep.org"
        #self.download.root = "cvs/lcio"

        self.envcmake["INSTALL_JAR"]="ON"

    def compile(self):
        """ compile LCIO """
        
        # ----- build with cmake -----
        if( self.useCMake ):
            
            os.chdir( self.installPath+'/build' )
            
            if self.rebuild:
                tryunlink( "CMakeCache.txt" )

            if( os.system( self.genCMakeCmd() + " 2>&1 | tee -a " + self.logfile ) != 0 ):
                self.abort( "failed to configure!!" )

            if( os.system( "make ${MAKEOPTS} 2>&1 | tee -a " + self.logfile ) != 0 ):
                self.abort( "failed to compile!!" )

            if( os.system( "make install 2>&1 | tee -a " + self.logfile ) != 0 ):
                self.abort( "failed to install!!" )

            # execute ctests
            if( self.makeTests ):
                
                if( os.system( "make tests && make test" ) != 0 ):
                    self.abort( "failed to execute lcio tests" )

        # ----- build with ant -----
        else:

            os.chdir( self.installPath )
            
            if self.rebuild:
                os.system( "ant clean" )
            
            if( os.system( "ant aid.generate 2>&1 | tee -a " + self.logfile ) != 0 ):
                self.abort( "failed to generate header files!!" )

            if( self.buildJava ):
                if( os.system( "ant aid 2>&1 | tee -a " + self.logfile ) != 0 ):
                    self.abort( "failed to execute ant aid!!" )

            if( os.system( "ant cpp 2>&1 | tee -a " + self.logfile ) != 0 ):
                self.abort( "failed to execute ant cpp!!" )

            if( self.buildFortran ):
                if( os.system( "ant f77 2>&1 | tee -a " + self.logfile ) != 0 ):
                    self.abort( "failed to execute ant f77!!" )

            if( self.buildDoc ):
                # check for doc tools
                if( not isinPath("javadoc")):
                    print "*** WARNING: javadoc was not found!! Part of the " + \
                        self.name + " documentation will not be built!!! "
                if( not isinPath("doxygen")):
                    print "*** WARNING: doxygen was not found!! Part of the " + \
                        self.name + " documentation will not be built!!! "
                if( not isinPath("latex")):
                    print "*** WARNING: latex was not found!! Part of the " + \
                        self.name + " documentation will not be built!!! "

                # build documentation
                print 80*'*' + "\n*** Building documentation for " + self.name + "...\n" + 80*'*'
                
                if( self.buildJava ):
                    if(isinPath("javadoc")):
                        print 80*'*' + "\n*** Creating JAVA API documentation for " + \
                            self.name + " with javadoc...\n" + 80*'*'
                        os.system( "ant doc 2>&1 | tee -a " + self.logfile )
                
                if(isinPath("doxygen")):
                    print 80*'*' + "\n*** Creating C++ API documentation for " + \
                        self.name + " with doxygen...\n" + 80*'*'
                    os.system( "ant cpp.doc" )
                
                if(isinPath("latex")):
                    print 80*'*' + "\n*** Creating " + self.name + " manual (from tex)...\n" + 80*'*'
                    r = os.system( "ant doc.manual 2>&1 | tee -a " + self.logfile )
                    if( r != 0 ):
                        print 80*'*' + "*** WARNING: sth. went wrong with creating the " + \
                            self.name + " manual\n" + 80*'*'
                    print 80*'*' + "\n*** Creating " + self.name + " reference manual (from api doc)...\n" + 80*'*'
                    r = os.system( "ant doc.ref 2>&1 | tee -a " + self.logfile )
                    if( r != 0 ):
                        print 80*'*' + "*** WARNING: sth. went wrong with creating the " + \
                            self.name + " reference manual\n" + 80*'*'


    def setMode(self, mode):
        BaseILC.setMode(self, mode)

        self.download.svnurl = 'svn://svn.freehep.org/lcio'

        if( Version( self.version ) == 'HEAD' ):
            self.download.svnurl += '/trunk'
        else:
            self.download.svnurl += '/tags/' + self.version



    def preCheckDeps(self):
        BaseILC.preCheckDeps(self)
       
        if( self.mode == "install" ):
            if( self.buildJava and not self.useCMake ):
                self.reqfiles.append(["lib/lcio.jar"])

            # tests
            if( self.makeTests ):
                self.envcmake.setdefault("BUILD_LCIO_TESTS","ON")
                self.envcmake.setdefault("BUILD_LCIO_EXAMPLES","ON")
                self.envcmake.setdefault("BUILD_F77_TESTJOBS","ON")

            #dc = self.envcmake.setdefault('BUILD_WITH_DCAP','OFF')

            #if dc == 'ON':
            #    self.addDependency( ['dcap'] )
            #    self.envcmake["DCAP_HOME"]=self.parent.module("dcap").installPath
                

    def postCheckDeps(self):
        BaseILC.postCheckDeps(self)

        self.env["LCIO"] = self.installPath

        # PATH
        self.envpath["PATH"].append( "$LCIO/tools" )
        self.envpath["PATH"].append( "$LCIO/bin" )
        self.envpath["LD_LIBRARY_PATH"].append( "$LCIO/lib" )


