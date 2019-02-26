# msclang

msclang is a custom compiler written in python made to compile C to MSC bytecode. MSC bytecode is a bytecode language used by Super Smash Brothers for Wii U in order to control character logic. It's name comes from the mix of "clang" a popular C compiler and, of course, MSC itself, however no part of clang is used and the name is only intended for pleasure of the user. This in no way indicates any affiliation with clang or it's developers.

### Requirements

* Python 3 (3.5 or higher suggested)
* pycparser (Can be obtained using `pip install pycparser`)

### Installation

* Extract contents (unit_tests folder not needed) anywhere
* Add that folder to PATH if it is not already
* Ensure the proper script (msclang.bat on windows, msclang.sh on linux) uses python 3 (by default it uses the `python` command, however this may need to be changed to `python3` or your system's equivelant)

### Features

msclang is based heavily on C but has lots of differences in order to best suite the target environment. While parsing follows the C99 standard, some features are missing. Here is a small list of differences:

* Types are primarily limited to int/string
* strings cannot be modified, only offered in a string literal. A string literal is held as a reference to the string in the form of an id in ascending order starting from 0. References should be held by the `int` type.
* While a type must be provided when declaring a variable much type leniency is given to the user.  
* `struct`s are non-existant
* Due to constraints of the bytecode there is no memory access. The only allowed type of pointer is function pointers which should be stored in the `int` type from which they can be called the same as in C.
* Global variables cannot have an initial value, any initial value must be set within a function.
* Some areas may not properly auto-cast between float and int. This is a bug, please report it in the issue tab.

### Notes

MSClang is currently a work in progress. Some features may be incomplete or missing. While bug reports of currently implemented features are most definitely appreciated, please avoid bug reports that relate to features missing entirely. 

[Follow me on twitter for updates, similar projects and jokes](https://twitter.com/jam1garner)

[Check out my medium for write ups on reverse engineering MSC (and probably other stuff)](https://medium.com/@jam1garner)
