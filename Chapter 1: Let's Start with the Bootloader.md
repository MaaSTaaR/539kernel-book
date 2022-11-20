---
title:  'A Journey in Creating an Operating System Kernel: The 539kernel Book'
author: 'Mohammed Q. Hussain'
---

# Chapter 1: Let's Start with the Bootloader {#ch-bootloader}

## Introduction
The first piece to start with when writing an operating system's kernel is the *boot loader* which is the code that is responsible for loading the main kernel from the disk to the main memory so the kernel can be executed. Before getting started with the details of the boot loader and all the other parts of the kernel, we need to learn a little bit about the tools (e.g. compilers and programming languages) that we will use in our journey of creating a kernel. In this chapter, we start with an overview of the tools and their basics and then we start with writing a boot loader.

## x86 Assembly Language Overview
To build a boot loader, we need to use assembly language. Also, there are some parts of an operating system kernel that cannot be written in a high-level language and the assembly language should be used instead as you will see later in this book. Therefore, a basic knowledge of the target architecture's assembly is required. In our case, the target architecture of our kernel is x86.

The program that takes the source code which is written in assembly language and transforms this code to the machine language is known as the *assembler* [^4]. There are many assemblers available for x86 but the one that we are going to use is Netwide Assembler (NASM). However, the concepts of x86 assembly are the same, they are tied to the architecture itself, also the instructions are the same, so if you grasp the basics it will be easy to use any other assembler [^5] even if it uses another syntax than NASM. Don't forget that the assembler is just a tool that helps us to generate executable x86 machine code out of the assembly code, so, any suitable assembler that we use to reach our goal will be enough.

In this section we don't aim to examine the details of x86 or NASM, you can consider this section as a quick start on both x86 and NASM. The basics will be presented to make you familiar with the x86 assembly language, more advanced concepts will be presented later when we need them. If you are interested in the x86 assembly for its own sake, there are various online resources and books that explain it in great detail.

### Registers
In any processor architecture, and x86 is not an exception, a register is a small memory cell inside the processor's chip. Like any other type of memory (e.g. RAM), we can store data inside a register and we can read data from it. The registers are very small and very fast. The processor architecture provides us with multiple registers. In x86 there are two types of registers: general purpose registers and special purpose registers. In general purpose registers we can store any kind of data we want, while the special purpose registers are provided by the architecture for some specific purposes. We will encounter the second type later in our journey of creating the 539kernel.

x86 provides us with eight general purpose registers and to use them in order to read from or write to them we refer to them by their names in assembly code. The names of these registers are: `EAX`, `EBX`, `ECX`, `EDX`, `ESI`, `EDI`, `EBP`, and `ESP`. While the registers `ESI`, `EDI`, `EBP` and `ESP` are considered to be general purpose registers in the x86 architecture ^[According to Intel's manual.], we will see later that they store some important data in some cases and it's better to use them carefully when we need to.

The size of each one of x86's general purpose registers is `32` bits (`4` bytes) and due to that, they are available only on x86 processors that support the `32-bit` architecture [^6] such as Pentium 4 for instance. These `32-bit` registers are not available on x86 processors that support only the `16-bit` architecture or lower, so, for example, you can't use the register `EAX` in Intel 8086 because it is a `16-bit` x86 processor and not a `32-bit` processor.

In old days, when the `16-bit` x86 processors were dominant, assembly programmers used the registers `AX`, `BX`, `CX` and `DX`. Each one of them used to have (and still has) the size of `16` bits (`2` bytes). But when the `32-bit` x86 processors arrived, these registers have been extended to have the size of `32` bits and their names were changed to `EAX`, `EBX`, `ECX` and `EDX`. The first letter `E` of the new names means *extended*. However, the old names are still usable in `32-bit` x86 processors and they are used to access and manipulate the first `16` bits of the corresponding registers. For instance, to access the first `16` bits of the register `EAX`, the name `AX` can be used. Furthermore, the first `16` bits of these registers can be divided into two parts and each one of the parts has the size of `8` bits (`1` byte) and has its own name that can be referred to in the assembly code. The first `8` bits of a register are called the *low* bits, while the second `8` bits are called the *high* bits.

Let's take one of these registers as an example: the `AX` register is a `16-bit` register which is a part of the bigger `32-bit` `EAX` register in the `32-bit` architecture. `AX` ^[Or in other words for the `32-bit` architecture: the first `16` bits of `EAX`.] is divided into two more parts, `AL` for the **l**ow `8` bits as the second letter of the name indicates and `AH` for the **h**igh `8` bits as the second letter of the name indicates. The same division holds true for the registers `BX`, `CX` and `DX`, figure @fig:26012022_0 illustrates that division.

![How the Registers `EAX`, `EBX`, `ECX` and `EDX` are Divided in x86](Figures/bootloader-ch/Fig26012022_0.png){#fig:26012022_0 width=50%}

### Instruction Set
The processor's architecture provides the programmer with *instructions* that can be used in assembly code. Processor's instructions resemble functions [^7] in high-level languages which are provided by libraries. In our case, we can consider the processor as the ultimate library for the assembly code. As with functions in high-level programming languages, each instruction has a name and performs a specific job. Also, it can take parameters which are called *operands*. Depending on the instruction itself, the operands can be static values (e.g. a number), register names that the instruction is going to fetch the stored value from or even memory locations.

The assembly language is really simple. The assembly code is simply a sequence of instructions which will be executed sequentially. The following snippet shows an example of assembly code, don't worry about its functionality right now, you will understand what it does eventually:

```{.asm}
mov ah, 0Eh
mov al, 's'
int 10h
```

As you can see, each line starts with an instruction which is provided to us by the x86 architecture. In the first two lines we use an instruction named `mov` and as you can see, this instruction receives two operands which are separated by a comma. In the shown usage of this instruction we can see that the first operand is a register name while the second operand is a static value. The third line uses another instruction named `int` which receives one operand. When this code is running, it will be executed by the processor sequentially, starting from the first line until it finishes in the last line.

If you are interested on the available instructions on x86, there is a four-volumes manual named "Intel® 64 and IA-32 architectures software developer's manual" provided by Intel that explains each instruction in detail [^9].

#### Assigning Values with `mov`
You can imagine a register to be an equivalent of a variable in high-level languages. We can assign values to a variable, we can change its old value and we can copy its value to another variable. In assembly language, these operations can be performed by the instruction `mov` which takes the value of the second operand and stores it in the first operand. You have seen in the previous examples the following two lines that use the `mov` instruction:

```{.asm}
mov ah, 0Eh
mov al, 's'
```

Now you can tell that the first line copies the value `0Eh` to the register `ah`, and the second line copies the character `s` to the register `al`. The single quotes are used in NASM to represent strings or characters and that's why we have used them in the second line. Based on that, you may have noticed that the value `0Eh` is not surrounded by single quotes though it contains characters. In fact, this value isn't a string, it is a number that is represented in the hexadecimal numbering system and due to that the character `h` was put at the end of that value. That is, putting `h` at the end of `0E` tells NASM that this value is a hexadecimal number. The equivalent number of `0E` in the decimal numbering system, which we humans use, is `14`, that is `0E` and `14` are the exactly the same number, but they are represented in two different numbering systems^[Numbering systems will be discussed in more details later.].

### NASM
Netwide Assembler (NASM) is an open-source assembler for the x86 architecture which uses Intel's syntax of assembly language. The other well-known syntax for assembly language is the AT&T syntax and, of course, there are some differences between the two. The first syntax is used in the official manuals of Intel. NASM can be used through the command line to assemble ^[The process of transforming an assembly source code to machine code is known as *assembling*.] x86 assembly code and generate the corresponding machine code. The basic usage of the NASM command is:

```
nasm -f <format> <filename> [-o <output>]
```

The argument `format` decides the binary format of the generated machine code, the binary format will be discussed in more details in a moment. The second argument is the `filename` of the assembly file that we would like to assemble. The last option and its argument are optional, we use them if we want to specify a specific name for the generated binary file. The default name will be same as the `filename` with a different extension.

#### Binary Format
The *binary format* is basically a specification which gives a blueprint of how a binary file is organized, in other words, it describes how a binary file is structured. In general there are multiple parts in a binary file and a binary format can be used to format them. The machine code is one part of a binary file. Note that each executable file uses some binary format to organize its contents and to make a specific operating system understand its contents. There are no differences between the programming languages in terms of the generated binary format [^prog-lang-and-bin] that will be used in the final output of the compiling process. For example on Linux, if we create a software either in C, Rust or assembly, the final executable result will be a binary file that is formatted by using a binary format known as *Executable and Linkable Format* (ELF) which is the default on Linux. There are many other binary formats, Mach-O is one example which is used by Mach-based [^mach-microkernel] operating systems, another example is Portable Executable (PE) which is used by Microsoft Windows.

Each operating system understands its own binary format well, and knows how a binary file that uses this format is structured, and how to seek the binary file to find the machine code that should be loaded into memory and executed by the processor. For example, when you run an ELF executable file on a GNU/Linux system, the Linux kernel will know it is an ELF executable file and assume that it is organized in a specific way. By using the specification of ELF, the Linux kernel will be able to locate the machine code of the software inside the ELF file and load it into memory and prepare it for execution.

In any binary format, one major part of the binary file that uses this format is the machine code that has been produced by compiling or assembling some source code. The machine code is specific to a processor architecture, for example, the machine code that has been generated for x64 [^x64] cannot run on x86. Because of that the binary files are distributed according to the processor architecture which they can run on. For example, GNU/Linux users see the names of software packages in the following format: `nasm_2.14-1_i386.deb`. The part `i386` indicates that the binary machine code of this package is generated for the `i386` architecture, which is another name for x86 by the way. That means this package cannot be used in a machine that uses an ARM processor such as the Raspberry Pi for example.

Due to that, to distribute a binary file for the same software for multiple processor architectures, a separate binary file should be generated for each architecture. To solve this problem, a binary format named `FatELF` was invented. In this binary format, the software machine code for different processor architectures is combined in one binary file and the suitable machine code will be loaded and executed based on the architecture of the system's processor. Naturally, the size of the files that use such format will be bigger than the files that use a binary format that is oriented for just one processor architecture. Due to the bigger size, this type of binary formats is known as a *fat binary*.

Getting back to the `format` argument of NASM, if our goal of using assembly language is to produce an executable file for Linux for example, we will use `elf` as the value for the `format` argument. But we are working on low-level kernel development, so our binary files should be flat and the value of `format` should be `bin` to generate a *flat binary* file which doesn't use any specification. Instead, in flat binary files, the output of the assembler is stored as is without any additional information or organization, they contain only the assembled machine code based on our source code. Using a flat binary for the bootloader makes sense because the code that is going to load ^[Which is the BIOS as we will see later.] our binary file doesn't understand any binary format. It can't interpret a binary format and it can't fetch the machine code out of it. Instead, the contents of the binary file will be loaded to the memory as is.

## GNU Make
GNU Make is a build automation tool. Well, don't let this fancy term make you panic! The concept behind it is very simple. When we create a kernel of an operating system ^[Or any software with any other compiled programming language.] we are going to write some assembly code and C code and both of them need to be assembled and compiled (for the C code) to generate the machine code as binary files. Each time a modification is made in the source code, you need to recompile (or reassemble) the modified code over and over again by executing the same commands in the terminal in order to regenerate the final binary output for your modified code. Besides the compiling and recompiling steps, an important step needs to take place in order to generate the final output, an operation known as *linking*. Usually a programming project contains multiple source files that reference each other, compiling each one of these files is going to generate a separate *object file* [^object_files] for each source file. During the linking process, these different object files are linked with each other to generate one binary file out of these multiple object files, the final binary file that represents the program that we are writing.

The operations which are needed to generate the final binary file out of the source code are known as the *build process*, which, as mentioned earlier, involves executing multiple commands such as compiling, assembling and linking. The build process is a tedious and error-prone job and to save our time (and ourselves from boredom of course) we don't want to write all these commands over and over again in order to generate the final output. We need an alternative and here's where GNU Make ^[And any other build automation tool.] comes to the rescue. It *automates* the *build* process by gathering all required commands in a text file known as the `Makefile` and once the user runs this file through the command `make`, GNU Make is going to run the specified commands sequentially. Furthermore, it will check whether a source code file was modified since the last time the build process was started, and if a file wasn't modified it won't be processed again and the generated object file from the last build process run will be used instead. This, of course, minimizes the time needed to finish the build process by preventing running unnecessary build steps.

### Makefile
A `Makefile` is a text file that tells GNU Make the needed steps to complete the build process of a specific source code file. `Makefile`s have a specific syntax, we should follow this syntax when writing a `Makefile`. A number of *rules* may be defined, we can say that a `Makefile` has a list of rules that define how to create the executable file. Each rule has the following format:

```{.makefile}
target: prerequisites
    recipe
```

When we run the command `make` without specifying a defined target name as an argument, GNU Make is going to start with the first rule in the `Makefile` whose target name doesn't start with a dot.It will skip all rules that have a target name starting with a dot. The name of a target can be any custom name or a filename. Assume that we defined a rule with the target name `foo` and it's not the first rule in the `Makefile`. We can tell GNU Make to execute this rule by running the command `make foo`. One of the well-known conventions when writing a `Makefile` is to define a rule with the target name `clean` that deletes all object files and binaries that have been created in the last building process. We will soon see the case where the name of a target is a filename instead of a custom name.

The `prerequisites` part of a rule is what we can call the list of dependencies. Those dependencies can be either filenames (the source code C files for instance) or other rules in the same `Makefile`. For GNU Make, to run a specific rule successfully, the dependencies of this rule should be fulfilled. If there is another rule in the dependencies of a rule, it should be executed successfully first. If there is a filename in the list of dependencies and there is no rule that matches the filename as its target name, then this file will be checked and used in the recipe of the rule.

Each line in the `recipe` part should start with a `tab` character. It contains the commands that will be run when the rule is being executed. These commands are normal Linux commands, so in this part of a rule we are going to write the compiling commands to compile the C source files, assembling commands for the assembly source files and the linking command that links the generated object files. Any arbitrary command can be used in the recipe as we will see later when we create the `Makefile` of the 539kernel. Consider the following C source files, the first one is `file1.c`, the second one is `file2.h` and the third one is `file2.c`:

```{.c}
#include "file2.h"
int main()
{
	func();
}
```

```{.c}
void func();
```

```{.c}
#include <stdio.h>
void func()
{
	printf( "Hello World!" );
}
```

By using these three files, let's look at an example of a `Makefile` that has no rules defined with target names that match the filenames above:

```{.makefile}
build: file1.c file2.c
	gcc -o ex_file file1.c file2.c
```

The target name of this rule is `build`, and since it is the first and only rule in the `Makefile` and its name doesn't start with a dot, it will be executed directly once the command `make` is issued. Another way to execute this rule is by mentioning its name explicitly as an argument to the `make` command as the following: `make build`.

The rule `build` depends on two C files, `file1.c` and `file2.c`, they should be available in the same directory. The recipe uses GNU GCC to compile and link these two files and generate an executable file named `ex_file`. The following is an example of a `Makefile` that has multiple rules:

```{.makefile}
build: file2.o file1.o
	gcc -o ex_file file1.o file2.o
file1.o: file1.c
	gcc -c file1.c
file2.o: file2.c file2.h
	gcc -c file2.c file2.h
```

In this example, the first rule `build` depends on two object files `file1.o` and `file2.o`. Before having executed the build process for the first time, these two files will not be available in the source code directory ^[Since they are a result of one step of the build process which is the compiling step that has not been performed yet.]. Therefore, we have defined a rule for each one of them. The rule `file1.o` is going to generate the object file `file1.o` and it depends on the file `file1.c`. The object file will simply be generated by compiling `file1.c`. The same happens with `file2.o` but this rule depends on two files instead of only one.

GNU Make also supports variables which can simply be defined with the following syntax: `foo = bar` and they can be used in the rules like the following: `$(foo)`. Let's now redefine the second `Makefile` by using variables:

```{.makefile}
c_compiler = gcc
build_dependencies = file1.o file2.o
file1_dependencies = file1.c
file2_dependencies = file2.c file2.h
bin_filename = ex_file
build: $(build_dependencies)
	$(c_compiler) -o $(bin_filename) $(build_dependencies)
file1.o: $(file1_dependencies)
	gcc -c $(file1_dependencies)
file2.o: $(file2_dependencies)
	gcc -c $(file2_dependencies)
```

## The Emulators
While developing an operating system kernel, for sure, you will need to run that kernel to test your code frequently. That of course can be done by writing the image of the kernel on a bootable device and reboot you machine over and over again in order to run your kernel. Obviously, this way isn't practical and needs a lot of chore work. Moreover, when a bug shows up, it will be really hard to debug your code by using this way. An alternative better way is to use an emulator to run your kernel every time you need to test it.

An emulator is a software that acts like a full computer and by using it you can run any code that requires to run on bare metal hardware. Also, by using an emulator, everything will be virtual. For example, you can create a virtual hard disk (that is, not real) that can be used by your kernel. This virtual hard disk will be a normal file on you host system, so, if anything goes wrong in your code you will not lose your data on your main system. Furthermore, an emulator can provide you with a debugger which will make your life a lot easier when you need to debug your code.

There are two options for the emulator, QEMU ^[<https://www.qemu.org/>] and Bochs ^[<https://bochs.sourceforge.io/>]. Both of them are open source and both of them provide us with a way to run a debugger. Personally, I liked Bochs' debugger better since it provides an easy GUI that saves a lot of time. QEMU on the other hand, gives its user the ability to use GNU Debugger through the command line. Running a kernel image is simple in QEMU, the following command performs that:

```
qemu-system-x86_64 kernel.img
```

Where `kernel.img` is the binary file of the kernel and the bootloader. You will see later in the 539kernel's `Makefile` that the option `-s` is used with QEMU, it can be safely removed but it is used to make GNU debugger able to connect to QEMU in order to start a debugging session. Of course you can find a lot more about QEMU in its official documentation ^[<https://www.qemu.org/docs/master/>].

To run your kernel by using Bochs, you need to create a configuration text file named `bochsrc`. Each time you run Bochs it will use this configuration file which tells Bochs the specification of the virtual machine that will be created. This specification provides information about the virtual processors, their number, their available features, the number of available virtual disks, their options, the path of their backing files and so on. Also, whether the debugger of Bochs and its GUI is enabled or not is decided through this configuration file. This configuration can be easily created or edited by using a command line interface by running the command `bochs` with no arguments. After creating the file you can use the option `-f bochsrc` where `bochsrc` is the filename of the configuration file to run your kernel directly with no questions from Bochs about what to do.

## Writing the Boot Loader
When a computer powers on, a piece of code named the bootloader is loaded and takes the control of the computer. Usually, the goal of the bootloader is loading the kernel of an operating system from the disk to the main memory and to give the kernel control over the computer. The firmware of a computer is the program which loads the bootloader, in IBM-compatible computers the name of this firmware is BIOS (Basic Input/Output System) ^[Before the advent of UEFI.].

There is a place on the hard disk called *boot sector*, it is the first sector of a hard disk ^[As we will see later, a magnetic hard disk has multiple stacked *platters*, each platter is divided into multiple *tracks* and inside each track there are multiple *sectors*.]. The BIOS loads the contents of the boot sector as a first step of running the operating system. Loading the boot sector's contents means that the BIOS reads the contents from the hard disk and loads them into the main memory (RAM). The loaded contents from the boot sector should contain the bootloader, and once it's loaded into the main memory, the processor will be able to execute it like any other code that we use in our computers. So, the last step performed by the BIOS in the booting process is giving the control to the bootloader to do whatever it wants.

Before getting started with writing the 539kernel, we need to write the bootloader that is going to load the 539kernel from the disk. In IBM-compatible PCs that use the BIOS to perform the booting process, the size of the bootloader is limited to `512` bytes and due to this limited size and the need of using low-level services, the bootloader is usually written in assembly language. Also, because of this limited size, we cannot depend on the BIOS to load the 539kernel instead of the bootloader and that's because a kernel is usually bigger than `512` bytes. Therefore, a small bootloader is loaded by the BIOS in order to load the bigger piece of code which is the kernel. The reason of this limited size of the bootloader is due to the size of a sector on the hard disk itself. Each sector on the hard disk has the size of `512` bytes and as we have mentioned, the BIOS is going to load the contents of the first sector of the hard disk, the boot sector, which, of course, like any other sector has the size of `512` bytes. 

Beside the bootloader's limited size, it is going to run in an *x86 operating mode* known as *real mode* ^[The concept of x86 operating modes and the real mode will be discussed in more details later.]. What we need to know about that for now is that the real mode is a `16-bit` environment, so, even if the processor is a `64-bit` processor, we can only use `16-bit` features of the processor, such as the registers of size `16` bits.

The booting process is too specific to the computer architecture as we have seen and it may differ between one architecture and another. Some readers, especially computer science students may notice that the academic textbooks of operating systems don't mention the bootloader or discuss it.

### Hard Disk Structure
A hard disk consists of multiple *platters* which are stacked together one above the other. Have you ever seen a CD or a DVD? A platter has exactly the same shape, refer to Figure @fig:a-platter. The both surfaces (top and down) of a platter are covered by a magnetic layer which stores the data. For each surface of a platter there is a read/write head on it, and as you guessed, the role of this head is to read from a surface or write to it. A head is attached to an arm. Those arms move horizontally, back and forth, and because the other ends of all of those arms are attached to the same physical part, they will be moved back and forth together to the same location at the same time. Figure @fig:platters-arms-heads shows how the platters, arms and read/write heads are assembled together.

![(A) Shows a platter when we see it from the side. (B) Shows a platter when we see it from top/down.](Figures/bootloader-ch/a-platter.png){#fig:a-platter width=50%}

The surface of a platter is divided into a number of tracks and each track is divided into a number of sectors. In Figure @fig:tracks-sectors you can see how tracks and sectors are organized on the surface, the gray circles that have the same center (cocentric) are the tracks, a track consists of smaller parts which are called sectors. A sector is the smallest unit that holds data on hard disks and as you know from our previous discussion, the first sector on a hard disk is known as the boot sector.

 ![Shows how the parts of a hard disk are assembled together.](Figures/bootloader-ch/platters-arms-heads.png){#fig:platters-arms-heads width=50%}

When a command is sent to the hard disk to write some data on it or read from it, at least two mechanical moves ^[This fancy term *mechanical moves* means that some physical part of a hard disk moves physically.] are performed. The first move is taken by the arms, they move back or forth in order to be upon the track that contains the data we would like to read. This operation is known as the *seek* operation. So, the *seek time* is the time needed to put a specific track under a read/write head. After finishing the seek operation, the read/write head will be on the right track but, also, it will be on a random sector ^[Not exactly random, can you tell why?]. To reach the sector that we would like to read from (or write to) the platter rotates until the read/write head becomes upon the required sector. The speed of rotation is measured by a unit known as *revolutions per minute* (RPM) and the needed time to reach the required sector is known as the *rotational latency*. Finally, the data will be *transferred* from the hard disk to the main memory, the time needed to transfer a number of bits is known as the *transfer time*.

Let's assume as an example a hard disk that has `3` platters, which means it has `6` surfaces, arms and read/write heads. When the operating system requests from the hard disk to seek a specific track, for instance track `3`, all `6` heads will seek the track `3` and when the seek operation ends, the `6` heads will point to the same physical position on all `6` surfaces. That is, the top head of the first platter and the bottom head of it will point to that same place, but the first one will be on the top surface while the second will be on the bottom surface, and so on for the other `4` remaining heads. The collection of all these tracks that the heads point to at some point in time is called a *cylinder*.

![Shows Tracks and Sectors on a platter's surface.](Figures/bootloader-ch/tracks-sectors.png){#fig:tracks-sectors width=50%}

Now, based on what we know about how a hard disk works, can we imagine what happens inside the hard disk when the BIOS loads a bootloader? First, the arms will seek the track number `0` ^[We didn't mention that previously, but yes, the bootloader resides in track `0`.], that is, the arms move back or forth until they reach the track `0`, then the platter rotates until the read/write head becomes upon the sector `0`, finally, the contents of sector `0` are transferred to the main memory.

### BIOS Services
We are on a journey of writing an operating system kernel, which means that we are dealing with a somewhat harsh environment! Do you remember all libraries that we are lucky to have when developing normal software (user-space software)? Well, none of them are available to us right now! And they will not be available until we decide to make them and work hard to achieve that. Even the simple function `printf` of C is not available.

But that's fine, to our luck, in this environment, where there is precious little available for us to write our code, the BIOS provides us with a bunch of useful services that we can use in real mode. We can use these services in our bootloader to get things done.

The BIOS services are like a group of functions in high-level languages that is provided by some library. Each function does something useful and we deal with those functions as black boxes. We don't know what's inside of those functions but we know what they do and how to use them. So, basically, the BIOS provides us a library of functions and we are going to use some of these functions in our bootloader.

The BIOS services are divided into categories. There is the video services category, the disk services category, the keyboard services category and so on. Each category is identified by a unique number called the *interrupt number*. In the high-level world, we witnessed the same concept but with a different mechanism. The C standard library, for example, provides us with many services (functions) such as input/output functions, string manipulation functions, mathematical functions and so on. These functions are categorized and each category is labelled by the *library name*. For example, all input/output functions can be found in `stdio.h` and so on. In the BIOS, for example, the category of video services has the interrupt number `10h`. As mentioned earlier, the letter `h` after a number means that this number is represented in the hexadecimal numbering system, or for short, a hexadecimal number. Here, `10h` doesn't equal the decimal number `10`, it equals the decimal number `16`. We already said that when a hexadecimal number is mentioned we use `h` as a postfix. Also, `0x` ^[The C programming language, for instance, uses this representation for hexadecimal numbers.] can be used as a prefix instead of `h`, so `10h` and `0x10` are equivalent.

Inside each services category, there are a bunch of services, each one can do a specific thing and each one is identified by a number. Continuing with the C analogy, a service is a function labeled by a name (e.g. `printf`) and this function resides in a library (e.g. `stdio.h`) which is the same as a category of services in the BIOS. As we said, the interrupt number `10h` represents the category of video services, and the service of printing a character on the screen (function) is represented by the number `0Eh`.

Interrupts are a fundamental concept in the x86 architecture. What we need to know about them right now is that there is a way to call the specific code which is assigned to the interrupt number. Calling an interrupt in assembly is really simple, the instruction `int` is used like the following: `int 10h`. That's it! We use the instruction `int` and give it the interrupt number as the first operand that represents the code that we would like to call. In this example, we are calling the code of the interrupt `10h` which is, as we mentioned multiple times, the category of BIOS video services. When the CPU executes this instruction, the BIOS will be called and based on the interrupt number it will know that we want to use one of the available video services, but which one exactly?

In the previous example, we actually didn't tell BIOS which video service we would like to use. To do that we need to specify a service number in the `AH` register before calling the interrupt:

```{.asm}
mov ah, 0Eh
int 10h
```

That's it, all the BIOS services can be used in this exact way. First we need to know what is the interrupt number that the service belongs to, then, we need to know the number of the service itself. We put the service number in the register `AH` then we call the interrupt by its number by using the `int` instruction.

The previous code calls the service of printing a character on the screen, but is it complete yet? Actually no, we didn't specify the character that we would like to print. We need something like parameters in high-level languages to pass additional information for the BIOS to be able to do its job. Well, lucky us! The registers are here to the rescue.

When a BIOS service needs additional information, that is, parameters, it expects to find this information in a specific register. For example, the service `0Eh` in interrupt `10h` expects to find the character that the user wants to print in the register `AL`, so, the register `AL` is one of the parameters of the service `0Eh`. The following code requests the BIOS to print the character `S` on the screen:

```{.asm}
mov ah, 0Eh
mov al, 'S'
int 10h
```

### A Little Bit More of x86 Assembly and NASM
We need to learn a couple more things about x86 assembly to be able to start. In NASM, each line in the source code has the following format:

```{.asm}
label: instruction operands
```

The label is optional, the operands depend on the x86 instruction in use, if it doesn't expect any operand then we don't need to write it. To write comments in NASM we begin with a semi-colon and write whatever we like after it as a comment and the rest of the source line will be considered a part of the comment.

A label is a way to give an instruction or a group of instructions a meaningful name. We can then use this name in other places in the source code to refer to this instruction/group of instructions. We can use labels for example to call this group of instructions or to get the starting memory address of these instructions. Sometimes, we will use labels to make the code more readable.

We can say that a label is something like the name of a function or a variable in C. As we know a variable name in C is a meaningful name that represents the memory address of a location in the main memory that contains the value of a variable. The same holds true for a function name. Labels in NASM work in the same way, under the hood they represent a memory address. The colon in a label is also optional.

```{.asm}
print_character_S_with_BIOS:
    mov ah, 0Eh
    mov al, 'S'
    int 10h
```

You can see in the code above, we gave a meaningful name for the group of instructions that print the character `S` on the screen. After defining this label in our source code, we can use it anywhere in the same source code to refer to this group of instructions.

```{.asm}
call_video_service int 10h
```

This is another example of labels. This time we eliminated the optional colon in the label's name and the label here points to only one instruction. Please note that extra whitespaces and newlines don't matter in NASM, so, the following example is equivalent to the one above:

```{.asm}
call_video_service
    int 10h
```

Consider the following code, what do you think it does?

```{.asm}
print_character_S_with_BIOS:
    mov ah, 0Eh
    mov al, 'S'

call_video_service:
    int 10h
```

It still prints `S` on the screen. Introducing labels in the source code doesn't change its flow, the code will be executed sequentially whether we used the labels or not. The sequence of execution will not be changed by merely using labels, if we need to change the sequence of execution we need to use other methods than labels. You already know one of these methods which is calling an interrupt. So, we can say that labels are more general than a variable name or function name in C. A label is a human-readable name for a memory location which can contain anything, code or data!

#### Jump and Return Unconditionally
Let's start this section with a simple question. What happens when we call a function in C? Consider the following C code:

```{.c}
main()
{
    int result = sum( 5, 3 );

    printf( "%d\n", result );
}
```

Here, the function `main` calls the function named `sum`. This function resides in a different region in memory and by calling it we are telling the processor to go to this different region of memory and execute what's inside it. The function `sum` is going to do its job, and after that, in some magical way, the processor is going to return to the original memory location where we called `sum` from and proceed the execution of the code that follows the call to `sum`, in this case, the `printf` function. How does the processor know where to return after completing the execution of `sum`?

The function which calls another function is named *caller* while the function which is called by the caller is named *callee*. In the above C code, the caller is the function `main` while the callee is the function `sum`.

##### A Glance on the Computer Architecture
When a program is started, a copy of its machine code is loaded in the main memory. This machine code is a sequence of instructions which the processor can understand and execute directly. These instructions are executed by the processor sequentially, that is, one after another in each cycle in the processor. Also, the data that the code being executed depends on is stored in the same main memory. This architecture where both code and data are stored in the same memory and the processor uses this memory to read the instructions that should be executed, and manipulates the data which is stored in the same memory is known as *von Neumann architecture*. There is another well-known architecture called the *Harvard architecture* where the code and data are stored in two different memories. x86 uses the *von Neumann architecture*.

When a processor starts a new *instruction cycle*, it fetches the next instruction that should be executed from the main memory and executes it ^[The instruction cycle is also called *fetch-decode-execute cycle*.]. Each *memory location* in the main memory is represented and referred to by a unique *memory address*, that means each instruction in the machine code of a loaded program has a unique memory address. Consider the following hypothetical example of memory addresses of each instruction in the previous C code (the memory addresses in this example are by no means accurate):

```{.c}
100 main() {
110    int result = sum( 5, 3 );
120    printf( "%d\n", result );
130 }

250 int sum( int firstNumber, int secondNumber ) {
260     return firstNumber + secondNumber;
270 }
```

The number on the left is the hypothetical memory address of the code line to the right, that means the function `main` starts from the memory address `100` and so on. Also, we can see that the callee `sum` resides in region of memory that is far away from the caller `main`.

The *Program Counter* is the part of the computer architecture that stores the *memory address* for the instruction that will be executed in the next instruction cycle of the processor. In x86, the program counter is a register known as the *instruction pointer* and its name is `IP` in the `16-bit` operating mode and `EIP` in the `32-bit` operating mode.

When the above C code runs for the first time, the value of the instruction pointer will be `100`, that is, the memory address of the starting point of the `main` function. When the instruction cycle starts, it reads the value of the instruction pointer register `IP`/`EIP` which is `100`, it fetches the instruction which is stored in the memory location `100` and executes it ^[For the simplicity of explanation, the details of *decoding* have been glossed over.]. Then the memory address of the next instruction `110` will be stored in the instruction pointer register for the next instruction cycle. When the processor finishes the execution of the instruction of the memory location `110`, this time, the value of `IP`/`EIP` will be `250` instead of `120` because, you know, we are calling the function `sum` which resides in the memory location `250`.

Each running program has a *stack* which is a region of the program's memory ^[The stack as a region of memory (x86 stack) is not same as the *data structure* stack, the former implements the latter.], that is, a place in memory that belongs to the program and can store data. We will examine the details of the stack later, but what is important for us at the moment is the following: when another function is called, in our case the function `sum`, the memory address of the next instruction of the callee `main` is *pushed* ^[Push means store something on a stack. This term is applicable for both the x86 stack and the data structure stack. As we have said previously, the x86 stack is an implementation of the stack data structure.] onto the stack. So the memory address `120` will be pushed onto the stack before calling `sum`. This address is called the *return address*. Now, assume that the processor is executing the instruction in the memory location `270`, that is, finishing the execution of the callee `sum`. After that the processor will find the return address which is `120` on the stack, get it and put it in the register `IP`/`EIP` for the next instruction cycle ^[By the way, this is, partially, the cause of buffer overflow bugs.]. So, this is the answer of our original question in the previous section "How does the processor know where to return after completing the execution of `sum`?".

##### The Instructions `call` and `ret`
The instruction `call` in assembly works exactly in the same way as our explanation in the previous section, it is used to call into the code that resides at a given memory address. The instruction `call` pushes the return address onto the stack and to return to the caller, the callee should use the instruction `ret` when it finishes. The instruction `ret` gets the return address from the stack ^[Actually it *pop*s the value since we are talking about a stack here.] and uses it to resume the execution of the caller. Consider the following example:

```{.asm}
print_two_times:
    call print_character_S_with_BIOS
    call print_character_S_with_BIOS
    ret

print_character_S_with_BIOS:
    mov ah, 0Eh
    mov al, 'S'
    int 10h
    ret
```

You can see here that we have used the code from the previous example for `print_character_S_with_BIOS` to define something like a C function by using the instructions `call` and `ret`. It should be obvious that the code of `print_two_times` prints the character `S` two times. As we have said previously, a label represents a memory address and `print_character_S_with_BIOS` is a label. The operand of `call` is the memory address of the code that we wish to call. The instructions under `print_character_S_with_BIOS` will be executed sequentially until the processor reaches the instruction `ret`, at this point, the return address is obtained from the stack and the execution of the caller is resumed.

The instruction `call` performs an *unconditional jump*, that means when the processor reaches a `call` instruction, it will always call the callee, without any condition. Later in this chapter we will see an instruction that performs a *conditional jump*, which only calls the callee when some condition is satisfied, otherwise, the execution of the caller continues sequentially with no flow change.

#### The One-Way Unconditional Jump
Like `call`, the instruction `jmp` jumps to the specified memory address, but unlike `call`, it doesn't store the return address in the stack which means `ret` cannot be used in the callee to resume the caller's execution. We use `jmp` when we want to jump to a code that we don't need to return from, `jmp` has the same functionality as the `goto` statement in C. Consider the following example:

```{.asm}
print_character_S_with_BIOS:
    mov ah, 0Eh
    mov al, 'S'
    jmp call_video_service

print_character_A_with_BIOS:
    mov ah, 0Eh
    mov al, 'A'

call_video_service:
    int 10h
```

Can you guess what the output of this code will be? It is `S` and the code of the label `print_character_A_with_BIOS` will never be executed because of the line `jmp call_video_service`. If we remove the line containing `jmp` from this code sample, `A` will be printed on the screen instead of `S`. Here is another example which causes an infinite loop:

```{.asm}
infinite_loop:
    jmp infinite_loop
```

#### Comparison and Conditional Jump
In x86 there is a special register called the *FLAGS* register ^[In `32-bit` x86 processors its name is *EFLAGS* and in `64-bit` its name is *RFLAGS*.]. It is the *status register* which holds the current status of the processor. Each usable bit of this register has its own purpose and name, for example, the first bit (bit `0`) of the FLAGS register is known as the *Carry Flag* (`CF`) and the seventh bit (bit `6`) is known as the *Zero Flag* (`ZF`).

Many x86 instructions use the `FLAGS` register to store their result in. One of those instructions is `cmp` which can be used to compare two integers which are passed to it as operands. When a comparison finishes, the processor stores its result in the `FLAGS` register. The following line compares the value which resides in the register `AL` with `5`: `cmp al, 5`.

Now, let's say that we would like to jump to a piece of code only if the value of `AL` equals `5`, otherwise, the code of the caller should continue without jumping. There are multiple instructions that perform *conditional* jumps based on the result of `cmp`. One of these instructions is `je` which means *jump if equal*. That is, if the two operands of the `cmp` instruction are equal, then jump to the specified code. Another conditional jump instruction is `jne` which means *jump if not equal*. There are other conditional jump instructions to handle the other cases. We can see that the conditional jump instructions have the same functionality of an `if` statement in C. Consider the following example:

```{.asm}
main:
    cmp al, 5
    je the_value_equals_5
    ; The rest of the code of `main` label
```

This example jumps to the code of the label `the_value_equals_5` if the value of the register `AL` equals `5`. In C, the above assembly example will be something like the following:

```{.c}
main() 
{
    if ( register_al == 5 )
        the_value_equals_5();

    // The rest of the code
}
```

Like `jmp`, but unlike `call`, conditional jump instructions don't push the return address onto the stack, which means the callee can't use `ret` to return and resume caller's code, that is, the jump will be a *one way jump*. We can also imitate a `while` loop by using conditional jump instructions and `cmp`, the following example prints `S` five times by looping over the same code:

```{.asm}
mov bx, 5

loop_start:
	cmp bx, 0
	je loop_end
	
	call print_character_S_with_BIOS
	
	dec bx
	
	jmp loop_start
	
loop_end:
	; The code after loop
```
You should be familiar with most of the code in this sample. First we assign the value `5` to the register `BX` ^[Can you tell why we used `BX` instead of `AX`? Hint: review the code of `print_character_S_with_BIOS`.], then we start the label `loop_start`. The first thing it does is comparing the value of `BX` with `0`, when `BX` equals `0` the code jumps to the label `loop_end` which contains the code after the loop, which means that the loop has ended. When `BX` doesn't equal `0` the label `print_character_S_with_BIOS` will be called to print `S` and return to the caller `loop_start`. After that the instruction `dec` is used to decrease `1` from its operand, that is `BX = BX - 1`. Finally, the label `loop_start` will be called again and the code repeats until the value of `BX` reaches `0`. The equivalent code in C is the following:

```{.c}
int bx = 5;

while ( bx != 0 )
{
    print_character_S_with_BIOS();
    bx--;
}

// The code after loop
```

#### Load String
We know that `1` byte equals `8` bits. Moreover, there are two size units in x86 other than a byte. The first one is known as a *word* which is `16` bits, that is, `2` bytes, and the second one is known as a *doubleword* which is `32` bits, that is, `4` bytes. Some x86 instructions have multiple variants to deal with these different size units. While the functionality of an instruction is the same, the difference will be in the size of the data that a variant of an instruction deals with. For example, the instruction `lods` has three variants `lodsb` which works a **b**yte, `lodsw` which works with a **w**ord and `lodsd` which works with a **d**oubleword.

To simplify the explanation, let's consider `lodsb` which works with a single byte. Its functionality is very simple, it reads the value of the register `SI` which is interpreted as a memory address by the instruction, then it transfers a byte from the contents of that memory address to the register `AL`, finally, it increments the value of `SI` by `1` byte. The same holds true for the other variants of `lods`, only the size of the data, the used registers and the increment size are different. The register which is used by `lodsw` is `AX` ^[Because the size of `AX` is a **word**] and `SI` is incremented by `2` bytes, while `lodsd` uses the register `EAX` ^[Because the size of `EAX` is a **doubleword**.] and `SI` is incremented by `4` bytes. ^[As an exercise, try to figure out why are we explaining the instruction `lodsb` in this chapter, what is the relation between this instruction and the bootloader that we are going to write? Hint: Review the code of `print_character_S_with_BIOS` and how to print a character by using BIOS services. If you can't figure out the answer don't worry, we'll get it soon.]

#### NASM's Pseudoinstructions
When you encounter the prefix ^[In linguistics, which is the science that studies languages, a prefix is a word (actually a morpheme) that is attached to the beginning of another word and changes its meaning, for example, in **un**do, **un** is a prefix.] *pseudo* in front of a word, you should know that it describes something fake, false or not real ^[For example, in algorithm design which is a branch of computer science, the term **pseudo**code means a code that is written in a fake programming language. Another example is the word **pseudo**science: A statement is pseudoscience when it is claimed to be a scientific fact, but in reality it is not, that is, it doesn't follow the scientific method.]. NASM provides us with a number of **pseudo**instructions, that is, they are not real x86 instructions, the processor doesn't understand them and they can't be used in other assemblers ^[Unless, of course, they are provided in the other assembler as pseudoinstructions.]. On the other hand, NASM understands those instructions and can translate them to something understandable by the processor. They are useful, and we are going to use them to make the writing of the bootloader easier.

##### Declaring Initialized Data
The concept of *declaring something* is well-known by the programmers. In C for example, when you *declare* a function, you are announcing that this function *exists*, it is there, it has a specific name and takes the declared number of parameters ^[It is important to note that *declaring* a function in C differs from *defining* a function, the following declares a function: `int foo();`. You can see that the code block (the implementation) of `foo` is not a part of the declaration, once the code block of the function is presented, we say this is the *definition* of the function.]. The same concept holds true when you declare a variable, you are letting the rest of the code know that there exists a variable with a specific name and type. When we declare a variable, without assigning any value to it, we say that this variable is *uninitialized*, that is, no initial value has been assigned to this variable when it was declared. Later on, a value will be assigned to the variable, but not at the time of its declaration. In contrast, a variable is *initialized* when a value is assigned to it when it's declared.

The pseudoinstructions `db`, `dw`, `dd`, `dq`, `dt`, `ddq` and `do` help us to initialize a memory location with some data, and by using labels we can mimic the concept of initialized variables in C. As an example, let's consider `db` which declares and initializes a byte of data, the second letter of `db` means *b*ytes:

```{.asm}
db 'a'
```

The above example reserves a byte in memory, this is the declaration step, then the character `a` will be stored in this reserved byte of memory, which is the initialization step.

```{.asm}
db 'a', 'b', 'c'
```

In the above example we have used commas to declare three bytes and store the values `a`, `b` and `c` respectively in them. In memory these values will be stored *contiguously*, that is, one after another. The memory location (hence, the memory address) of the value `b` will be right after the memory location of the value `a` and the same rule applies for `c`. Since `a`, `b` and `c` are of the same type, a character, we can write the previous code as the following and it produces exactly the same result:

```{.asm}
db 'abc'
```

Also, we can declare different types of data in the same source line. Given the above code, let's say that we would like to store the number `0` after the character `c`, this can be achieved by simply using a comma:

```{.asm}
db 'abc', 0
```

Now, to make this data accessible from other parts of the code, we can use a label to represent the starting memory address of this data. Consider the following example, it defines the label `our_variable`, after that, we can use this label to refer to the initialized data:

```{.asm}
our_variable db 'abc', 0
```

##### Repeating with `times`
To repeat some source line multiple times, we can use the pseudoinstruction `times` which takes the number of repetitions as the first operand and the instruction that we would like to execute repeatedly as the second operand. The following example prints `S` five times on the screen:

```{.asm}
times 5 call print_character_S_with_BIOS
```

Not only normal x86 instructions can be used with `times` as a second operand, also NASM's pseudoinstructions can be used with `times`. The following example reserves `100` bytes of memory and fills them with `0`:

```{.asm}
times 100 db 0
```

#### NASM's Special Expressions
In programming languages, an *expression* is the part of the code that evaluates a value, for example, `x + 1` is an expression, also, `x == 5` is an expression. On the other hand, a *statement* is the part of the code that performs some action, for example, in C, `x = 15 * y;` is a statement that assigns the result of an expression to the variable `x`.

NASM has two special expressions, the first one is `$` which points to the beginning of the *assembly position* of the current source line in memory. So, one way of implementing an infinite loop is the following: `jmp $`. The second special expression is `$$` which points to the beginning of the current *section* of assembly code.

### The Bootloader
As we discussed previously, the size of the bootloader should be `512` bytes, the firmware loads the bootloader at the memory address `07C0h`. Also, the firmware can only recognize the data in the first sector as a bootloader when that data finishes with the magic code `AA55h`. When the 539kernel's bootloader starts, it shows two messages to the user, the first one is `The Bootloader of 539kernel.` and the second one is `The kernel is loading...`. After that, it is going to read the disk to find the 539kernel and load it to memory. After loading the 539kernel to memory, the bootloader transfers control to the kernel by jumping to the start of the code of the kernel.

Right now, the 539kernel doesn't exist ^[Actually it does! But you know what I mean.], we haven't written it yet, so, in our current stage, instead of loading the 539kernel, the bootloader is going to load the code that prints `Hello World!, From Simple Assembly 539kernel!`. In this section, we are going to write two assembly files, the `bootstrap.asm` which contains the bootloader and `simple_kernel.asm` which is the temporary replacement for the 539kernel. Also, the `Makefile` which compiles the source code of the assembly files will be presented in this section.

#### Implementing the Bootloader
Until now, you have learned enough to understand most of the bootloader that we are going to implement, however, some details have not been explained in this chapter and have been delayed to be explained later. The first couple of lines of the bootloader use concepts that haven't been explained yet, our bootloader source code starts with the following code:

```{.asm}
start:
	mov ax, 07C0h
	mov ds, ax
```

First, we define a label named `start`, there is no practical reason to define this label (such as a target for a jump to it for example), the only reason of defining it is the readability of the code, when someone else tries to read the code, it should be obvious that `start` is the starting point of the bootloader execution.

The job of the next two lines is simple, we are moving the hexadecimal number `07C0` to the register `AX` then we move the same value to the register `DS` from `AX`. Note that we can't store the value `07C0` directly in `DS` by using `mov` like the following: `mov ds, 07C0h`. Due to that, we have to first put the value in `AX` and then moved it to `DS`. Our goal was to set the value `07C0` in the register `DS`, this restriction of not being able to store to `DS` directly is something that is decided by the processor architecture. Now, you may ask, why do we want to have the value `07C0` in the register `DS`? This is a story for another chapter, just take these two lines on faith, later you will learn their purpose. Let's continue.

```{.asm}
	mov si, title_string
	call print_string
	
	mov si, message_string
	call print_string
```

The block of code above prints the two messages that we mentioned earlier, they are represented by the labels `title_string` and `message_string`. You can see that we are calling the code of a label `print_string` that we didn't define yet. Its name indicates that it prints a *string* of characters, and you can infer that the function `print_string` receives the memory address of the string that we would like to print as a parameter in the register `si`. The implementation of `print_string` will be examined in a minute.

```{.asm}
	call load_kernel_from_disk
	jmp 0900h:0000
```

The two lines above represent the most important part of any bootloader. First a function named `load_kernel_from_disk` is called, we are going to define this function in a moment. As you can see from its name, it is going to load the code of the kernel from disk into the main memory and this is the first step that allows the kernel to take the control over the system. When this function finishes its job and returns, a jump is performed to the memory address `0900h:0000`, but before discussing the purpose of the second line let's define the function `load_kernel_from_disk`:

```{.asm}
load_kernel_from_disk:
	mov ax, 0900h
	mov es, ax
```

This couple of lines, also, should be taken on faith. You can see, we are setting the value `0900h` in the register `ES`. Let's move to the most important part of this function:

```{.asm}
	mov ah, 02h
	mov al, 01h
	mov ch, 0h
	mov cl, 02h
	mov dh, 0h
	mov dl, 80h
	mov bx, 0h
	int 13h
	
	jc kernel_load_error

	ret
```

This block of code **loads** the kernel from the disk into the memory and to do that it uses the BIOS service `13h` which provides services that are related to hard disks. The service number which is `02h` is specified in the register `AH`. This service reads sectors from the hard disk and loads them into the memory. The value of the register `AL` is the number of sectors that we would like to read. In our case, because the size of our temporary kernel `simple_kernel.asm` doesn't exceed `512` bytes, we read only `1` sector. Before discussing the rest of the values passed to the BIOS service, we need to mention that our kernel will be stored right after the bootloader on the hard disk, and based on this fact we can set the correct values for the rest of the registers which represent the disk location of the contents that we would like to load.

The value of the register `CH` is the number of the track that we would like to read from, in our case, it is the track `0`. The value of the register `CL` is the sector number that we would like to read, in our case, it is the second sector. The value of the register `DH` is the head number. The value of `DL` specifies the type of the disk that we would like to read from, the value `0h` in this register means that we would like to read the sector from a floppy disk, while the value `80h` means we would like to read from the hard disk `#0`, `81h` stands for the hard disk `#1`. In our case, the kernel is stored on the hard disk `#0`, so, the value of `DL` should be `80h`. Finally, the value of the register `BX` is the memory address that the contents will be loaded into. In our case, we are reading one sector, and its contents will be stored at the memory address `0h` ^[Not exactly the memory address `0h`, in fact, it will be loaded at the offset `0` inside a segment that starts at `0900h`. Don't worry, these details will be examined later in the next chapter \ref{ch-x86}.].

When the contents are loaded successfully, the BIOS service `13h:02h` is going to set the carry flag ^[Which is part of the `FLAGS` register as we mentioned earlier.] to `0`, otherwise, it sets the carry flag to `1` and stores the error code in register `AX`. The instruction `jc` is a conditional jump instruction that jumps when `CF = 1`, that is, when the value of the carry flag is `1`. That means our bootloader is going to jump to the label `kernel_load_error` when the kernel couldn't be loaded correctly.

If the kernel is loaded correctly, the function `load_kernel_from_disk` returns by using the instruction `ret` which tells the processor to resume the main code of our bootloader and to execute the instruction which is after `call load_kernel_from_disk`. This next instruction is `jmp 0900h:0000` which gives the control to the kernel by jumping to its starting point, that is, the memory location where we loaded our kernel to. This time, the operand of `jmp` is an **explicit** memory address `0900h:0000`. It has two parts, the first part is the one before the colon, you can see that it is the same value that we have loaded in the register `ES` at the beginning of the `load_kernel_from_disk` function. The second part of the memory address is the one after the colon, it is `0h` ^[Here, `0h` is equivalent to `0000`.] which is the *offset* that we have specified in the register `BX` in `load_kernel_from_disk` before calling `13h:02h`. Both parts combined represent the memory address that we have loaded our kernel into. The details of the two parts of this memory address will be discussed in chapter \ref{ch-x86}.

Now that we have finished the basic code of the bootloader, we can start defining the labels that we have used before in its code. We start with the label `kernel_load_error` which simply prints an error message. The function `print_string` is used to perform that. After printing the message, nothing more can be done, so, `kernel_load_error` enters an infinite loop:

```{.asm}
kernel_load_error:
	mov si, load_error_string
	call print_string
	
	jmp $
```

Our previous examples of using the BIOS service `10h:0Eh` were printing only one character. In real world, we need to print a **string** of characters and that's what the function `print_string` exactly does. It takes the memory address which is stored in the register `SI` and prints the character which is stored at this memory location, then it moves to the next memory address and prints the character which is stored at this next memory location and so on. That is, `print_string` prints a string character by character. So, you may ask, how can `print_string` know when it should stop?

A string in the C programming language, like in our situation, is an array of characters, and the same problem of "where does a string end" is encountered in C. To solve the problem, each string in C ends with a special character named the *null character* and is represented by the symbol `\0` in C ^[This type of string is named a *null-terminated string*.]. So, you can handle any string in C character by character and once you encounter the null character `\0` you know that you have reached the end of that string. We are going to use the same mechanism in our `print_string` function to recognize the end of a string by putting the value `0` as a marker at the end of it. By using this method, we can now use the service `10h:0Eh` to print any string, character by character, through a loop and once we encounter the value `0` we can stop the printing:

```{.asm}
print_string:
	mov ah, 0Eh

print_char:
	lodsb
	
	cmp al, 0
	je printing_finished
	
	int 10h
	
	jmp print_char

printing_finished:
	mov al, 10d ; Print new line
	int 10h
	
	; Read the current cursor position
	mov ah, 03h
	mov bh, 0
	int 10h
	
	; Move the cursor to the beginning
	mov ah, 02h
	mov dl, 0
	int 10h

	ret
```

When `print_string` starts, the BIOS service number `0Eh` is loaded in `AH`, this operation needs to execute just one time for each call of `print_string`, so it is not a part of the next label `print_char` which is also a part of `print_string` which will be executed right after moving `0Eh` to `AH`.

If you can remember, the parameter of `print_string` is the memory address which contains the beginning of the string that we would like to print. This parameter is passed to `print_string` via the register `SI`, so, the first thing `print_char` does is to use the instruction `lodsb` which is going to transfer the first character of the string to the register `AL` and increase the value of `SI` by `1` byte. After that, we check whether the character that has been transferred from the memory to `AL` is `0`, which means that we have reached the end of the string and the code jumps to the label `printing_finished`. Otherwise, the interrupt `10h` of BIOS is called to print the contents of the register `AL` on the screen. Then we jump to `print_char` again to repeat this operation until we reach the end of the string.

When printing a string finishes, the label `printing_finished` starts by printing a new line after the string. The new line is represented by the number `10` in ASCII. After that use the service `03h` to read the current position of the cursor, then we use the service `02h` to set the cursor position to `0` by passing it to the register `DL`. If we wouldn't do this, the messages in the new lines would be printed at the position where the previous string finished. Finally the function returns to the caller by using the instruction `ret`.

```{.asm}
title_string        db  'The Bootloader of 539kernel.', 0
message_string      db  'The kernel is loading...', 0
load_error_string   db  'The kernel cannot be loaded', 0
```

The code above defines the strings that have been used in the previous snippets. Note the last part of each string is the null character that indicates the end of a string ^[Exercise: What will be the behavior of the bootloader if we remove the null character from `title_string` and `message_string` and keep it only in `load_error_string`?].

Now, we have written our bootloader and the last thing to do is to put the *magic code* at the end of it. The magic code which is a `2` byte value that should reside in the last two bytes in the first sector, that is, in the locations `510` and `511` (the location numbering starts from `0`). Otherwise, the firmware will not recognize the contents of the sector as a bootloader. To ensure that the magic code is written at the correct location, we are going to fill the empty space between the last part of the bootloader code and the magic code with zeros, this can be achieved with the following line:

```{.asm}
times 510-($-$$) db 0
```

Here, the instruction `db` will be called `510-($-$$)` times. This expression gives us the remaining empty space in our bootloader before the magic code, and because the magic code is a `2` byte value, we subtract `($-$$)` from `510` instead of `512`. We will use the last two bytes for the magic code. The expression `($-$$)` uses the special expressions of NASM, `$` and `$$`, and it calculates the size of the bootloader code until the current line. Finally, the magic code is defined:

```{.asm}
dw 0xAA55
```

#### Implementing `simple_kernel.asm`

The `simple_kernel.asm` which the bootloader loads is very simple, it prints the message `Hello World!, From Simple Assembly 539kernel!`. We don't need to go through its code in detail since you already know most of it:

```{.asm}
start:
	mov ax, cs
	mov ds, ax

	; --- ;
	
	mov si, hello_string
	call print_string
	
	jmp $

print_string:
	mov ah, 0Eh

print_char:
	lodsb
	
	cmp al, 0
	je done
	
	int 10h
	
	jmp print_char

done:
	ret
	
hello_string db 'Hello World!, From Simple Assembly 539kernel!', 0
```

The only lines that you are not familiar with yet are the first two lines in the label `start` which will be explained in detail in chapter \ref{ch-x86}. Finally the `Makefile` is the following:

```{.makefile}
ASM = nasm
BOOTSTRAP_FILE = bootstrap.asm 
KERNEL_FILE = simple_kernel.asm

build: $(BOOTSTRAP_FILE) $(KERNEL_FILE)
	$(ASM) -f bin $(BOOTSTRAP_FILE) -o bootstrap.o
	$(ASM) -f bin $(KERNEL_FILE) -o kernel.o
	dd if=bootstrap.o of=kernel.img
	dd seek=1 conv=sync if=kernel.o of=kernel.img bs=512
	qemu-system-x86_64 -s kernel.img

clean:
	rm -f *.o
	rm -f kernel.img
```

[^4]: While the program that transforms the source code which is written in a high-level language such as C to machine code is known as the *compiler*.
[^5]: Another popular open-source assembler is GNU Assembler (GAS). One of the main differences between NASM and GAS is that the former uses Intel's syntax while the latter uses the AT&T syntax.
[^6]: Also they are available on `64-bit` x86 CPUs such as Core i7 for instance.
[^7]: Or a procedure for people who work with Algol-like programming languages.
[^9]: <https://software.intel.com/en-us/articles/intel-sdm>
[^object_files]: An object file is the machine code that is generated by the compiler out of a source file. The object file is not an executable file and in our case at least it has to be linked with other object files to generate the final executable file.
[^mach-microkernel]: Mach is an operating system kernel which is well-known for using the *microkernel* design. It has been started as a research effort at Carnegie Mellon University in 1985. Current Apple's operating systems macOS and iOS are both based on an older operating system known as NeXTSTEP which used Mach as its kernel.
[^prog-lang-and-bin]: Of course the programming language should be a *compiled* programming language such as C or Rust and not an *interpreted* one such as Python or one that uses a virtual machine such as Java.
[^x64]: The x86 architecture that supports 64-bit.
