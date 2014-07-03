#!/usr/bin/python
# -*- coding: utf-8 -*-

##############################################################################################################
# Takes a xwot specification and creates a valid WADL file #
# ---------------------------------------------------------------------------------------------------------- #
#                                                                                                            #
# Author: Andreas Ruppen                                                                                     #
# License: GPL                                                                                               #
# This program is free software; you can redistribute it and/or modify                                       #
#   it under the terms of the GNU General Public License as published by                                     #
#   the Free Software Foundation; either version 2 of the License, or                                        #
#   (at your option) any later version.                                                                      #
#                                                                                                            #
#   This program is distributed in the hope that it will be useful,                                          #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of                                           #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                            #
#   GNU General Public License for more details.                                                             #
#                                                                                                            #
#   You should have received a copy of the GNU General Public License                                        #
#   along with this program; if not, write to the                                                            #
#   Free Software Foundation, Inc.,                                                                          #
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.                                                #
##############################################################################################################
import os
import shutil
import string
import logging
import logging.config
import sys
if float(sys.version[:3])<3.0:
    import ConfigParser
else: 
    import configparser as ConfigParser
import xml.dom.minidom
import argparse
import codecs


class Model2Python:
    """
        Created on 27 June 2014
        @author: ruppena
    """
    def __init__(self):
        """Do some initialization stuff"""
        logging.basicConfig(level=logging.ERROR)
        logging.config.fileConfig('logging.conf')
        self.__log = logging.getLogger('thesis')

        
        self.__log.debug("Reading general configuration from Model2WADL.cfg")
        self.__m2wConfig = ConfigParser.SafeConfigParser()
        self.__m2wConfig.read("Model2WADL.cfg")
        #you could read here parameters of the config file instead of passing them on cmd line
        self.__baseURI = self.__m2wConfig.get("Config", "baseURI")
        self.__basePackage = self.__m2wConfig.get("Config", "basePackage")
        self.__schemaFile = self.__m2wConfig.get("Config", "schemaFile")
        
        
    def createServers(self,  node,  path):
        self.__log.debug(node)
        node_type = node.getAttribute('xsi:type')
        resourcePath = path+node.getAttribute('uri')+'/'
        resourcePath = resourcePath.replace('{',  '<int:').replace('}',  '>')
        if node_type == 'xwot:SensorResource' or  node_type == 'xwot:ActuatorResource' or node_type == 'xwot:ContextResource' or node_type == 'xwot:Resource':
            self.createPythonService(node, resourcePath)
        elif node_type == 'xwot:VResource':
            self.createNodeManagerService(node,  resourcePath)
            for child_node in self.getResourceNodes(node):
                node_type = child_node.getAttribute('xsi:type')
                if node_type == 'xwot:SensorResource' or  node_type == 'xwot:ActuatorResource' or node_type == 'xwot:ContextResource' or node_type == 'xwot:Resource':
                    resourcePath='/'
                self.createServers(child_node,  resourcePath)
            
    def createPythonService(self,  source,  path):
        # Todo create unique names for theses
        project_name = 'REST-Servers/'+path.replace('/', '_')+'Server'
        self.__log.debug(project_name)
        shutil.copytree('REST-Server-Skeleton',  project_name)
        self.addResourceDefinitions(source,  project_name,  "root")
        
        #Some Cleanup
        filein = open(project_name+'/rest-server.py')
        src = string.Template(filein.read())
        r = {'imports': "",  'pathdef':""}
        result = src.substitute(r)
        filein.close()
        service_file = open(project_name+'/rest-server.py', "w"   )
        service_file.write(result)
        #self.__log.debug(result)
        service_file.close()
        
    def addResourceDefinitions(self,  node,  project_path,  parent_classname):
        new_parent_classname = self.doAddResourceDefinitions(node,  project_path,  parent_classname)
        for resource in self.getResourceNodes(node):
            self.addResourceDefinitions(resource,  project_path,  new_parent_classname)
        
        
    def createNodeManagerService(self, source,  path):
        project_name = 'REST-Servers/NM-'+path.replace('/', '_')+'Server'
        self.__log.debug(project_name)
        shutil.copytree('REST-Server-Skeleton', project_name)
        self.addNodeManagerResourceDefinitions(source,  project_name,  "root")
        
        
        #Some Cleanup
        filein = open(project_name+'/rest-server.py')
        src = string.Template(filein.read())
        r = {'imports': "",  'pathdef':""}
        result = src.substitute(r)
        filein.close()
        service_file = open(project_name+'/rest-server.py', "w"   )
        service_file.write(result)
        service_file.close()
        
    def addNodeManagerResourceDefinitions(self,  node,  project_path,  parent_classname):
        new_parent_filename = self.doAddResourceDefinitions(node,  project_path,  parent_classname)
        for resource in self.getResourceNodes(node):
            filein = open(new_parent_filename)
            src = string.Template(filein.read())
            classname=resource.getAttribute('name')+"API"
            childSubstitute = "if name == '"+resource.getAttribute('uri').replace('{',  '<int:').replace('}',  '>')+"':"+'\n'+"            return "+classname+"(self.datagen, '')"+'\n'+"        $child"
            importSubstitue = "from "+classname+" import "+classname+'\n'+"$import"
            d = {'child':childSubstitute,  'import':importSubstitue}
            #self.__log.debug(childSubstitute)
            result = src.substitute(d)
            filein.close()
            class_file = open(project_path+'/'+node.getAttribute('name')+"API"+'.py',  'w')
            class_file.write(result)
            class_file.close()
            self.addNodeManagerResourceDefinitions(resource,  project_path,  new_parent_filename)
        filein = open(project_path+'/'+node.getAttribute('name')+"API"+'.py')
        src = string.Template(filein.read())
        r = {'classname':'',  'child':'',  'import':''}
        result = src.substitute(r)
        filein.close()
        service_file = open(project_path+'/'+node.getAttribute('name')+"API"+'.py', "w"   )
        service_file.write(result)
        service_file.close()
            
    def doAddResourceDefinitions(self, node,  project_path,  parent_classname):
        filein = open(project_path+'/resourceAPI.py')
        src = string.Template(filein.read())
        classname=node.getAttribute('name')+"API"
        d = {'classname':classname,  'child':'$child',  'import':'$import'}
        result = src.substitute(d)
        filein.close()
        class_file = open(project_path+'/'+classname+'.py',  'w')
        class_file.write(result)
        class_file.close()
        
        filein = open(project_path+'/rest-server.py')
        class_file_in = string.Template(filein.read())

        classnameClass=classname.lower()
        if parent_classname == "root":
            pathdef = classnameClass+"="+classname+"(data, '')"+'\n        '+parent_classname+".putChild('"+node.getAttribute('uri').replace('{',  '<int:').replace('}',  '>')+"',  "+classnameClass+")"+'\n        $pathdef'
        else:
            #pathdef = classnameClass+"="+classname+"(data, '')"+'\n        '+parent_classname+".putChild('"+node.getAttribute('uri').replace('{',  '<int:').replace('}',  '>')+"',  "+classnameClass+")"+'\n        $pathdef'
            pathdef = ''
        imports = "from "+classname+" import "+classname+'\n'+"$imports"

        r = {'imports':imports, 'pathdef':pathdef}
        class_file_in = class_file_in.substitute(r)
        class_file = open(project_path+'/rest-server.py', "w"   )
        class_file.write(class_file_in)
        class_file.close()
        filein.close
        return project_path+'/'+classname+'.py'
    
    def getResourceNodes(self,  parent):
        resources = []
        for child in parent.childNodes:
            if child.localName == 'Resource':
                resources.append(child)
        return resources
        
    def getNodeManagerResourceNodes(self,  parent):
        resources = []
        for child in parent.childNodes:
            if child.localName == 'VResource':
                resources.append(child)
        return resources
            
    def main(self):
        """The main function"""
        self.__log.debug("input File is: "+self.__input)
        self.__model = xml.dom.minidom.parse(self.__input)
        output_dir = 'REST-Servers'
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.mkdir(output_dir)
        ve = self.__model.getElementsByTagName('VirtualEntity')[0] 
        self.createServers(ve, '/')

    def getArguments(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument("-i",  "--input",  help="input xWoT file containing the Model to be translated",  required=True)
        args = parser.parse_args(argv)
        self.__input = args.input
        self.main()



if __name__ == "__main__":
    prog = Model2Python()
    prog.getArguments(sys.argv[1:])
