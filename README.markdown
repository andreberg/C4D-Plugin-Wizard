Introduction
------------

**CINEMA 4D Plugin Wizard** is a wizard UI application that utilizes a   
multi-purpose template system. 

What is a multi-purpose template system? Well, a template system is a   
framework for creating templates. And a multi-purpose template system   
is a system that doesn’t actually care what the template is trying to   
represent, what content it ought to have.

On the lowest level, all the program does is, it makes copies of a   
template folder structure which it then processes by going through all   
items inside that structure looking for certain kinds of text that it   
replaces with text supplied by the user. 

These text replacements are supported not only inside the contents of   
any type of file, but also inside the names of any file or folder found   
inside that template structure.

To read more about its intended purpose and design, I'll refer you to   
the [companion blog post](http://irisvfx.com/blog/programming/cinema-4d-plugin-wizard).

Documentation
-------------

You can find the documentation online at the following link: 

[Documentation](http://andreberg.github.io/C4D-Plugin-Wizard/index.html)

Installation
------------

Pre-compiled versions are available for OS X and Windows.

[Download for Windows](https://www.dropbox.com/sh/g8qpo2xewpdzb3v/Z67ofP1aCX/CINEMA_4D_Plugin_Wizard_%28Win%29.zip)  
[Download for OS X](https://www.dropbox.com/sh/g8qpo2xewpdzb3v/FzzBbDVLrZ/CINEMA_4D_Plugin_Wizard_%28OSX%29.zip)

Otherwise, if you want to compile yourself, you're gonna need a version   
of PyInstaller 2.0. Then just use the compilation script file for your   
operating system found under the `scripts` directory.

Basic Usage
-----------

Launch the app, enter your details, pick a template folder, select output   
directory and confirm.

A few templates are included as a starting point.

Copyright
---------

Copyright 2013, André Berg (Iris VFX)

License
-------

Licensed under the Apache License, Version 2.0 (the "License");  
you may not use this file except in compliance with the License.  
You may obtain a copy of the License at

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software  
distributed under the License is distributed on an "AS IS" BASIS,  
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
See the License for the specific language governing permissions and  
limitations under the License.  
