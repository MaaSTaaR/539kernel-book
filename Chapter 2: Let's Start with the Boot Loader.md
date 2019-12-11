# Let's Start with the Bootloader

## Introduction

When a computer powers on, a piece of code called bootloader is loaded and takes the control of the computer. Usually, the goal of the bootloader is loading the kernel of an operating system from the disk to the main memory and gives the kernel the control of the computer. The firmware of a computer is the program which loads the bootloader, in IBM-compatible computers the name of this program is BIOS (Basic Input/Output System) [^2].

There is a place in the hard disk called *boot sector*, it is the first sector of a hard disk [^3], BIOS is going to load the content of the boot sector as a first step of running the operating system. Loading the boot sector's content means that BIOS reads the content from hard disk and loads it into the main memory (RAM). This loaded content from the boot sector should be the boot loader, and once its loaded into the main memory, the CPU will be able to execute it as any normal application we use in our computers. So, the last step performed by BIOS in this process is giving the control to the bootloader to do whatever it wants.

So, before start writing 539kernel, we need to write the bootloader that is going to load 539kernel from the disk. In x86 architecture, the size of the bootloader is limited to 512 bytes and due to this restricted size and the need of using low-level services, the bootloader is usually written in assembly language. The reason of this limited size of the bootloader is because of the size of a sector in the hard disk itself. Each sector in the hard disk has the size of 512 bytes and as we have mentioned, BIOS is going to load the content of the first sector of hard disk, the boot sector, which, of course, as any sector its size is 512 bytes.

The booting process is too specific to the computer architecture as we have seen and it may differs between one architecture and another. Some readers, especially Computer Science students may notice that the academic textbooks of operating systems don't mention the boot loader or discuss it.

## Hard Disk Structure

The sectors of hard disk have been mentioned too quickly above, so, let's examine them in a little details now. 

## BIOS Services
When our bootloader loads, it is going to work on an x86 mode called *Real Mode* [^real-mode] which is a 16-bit operating mode, don't worry right now about these details, we are going to examine them. We are trying to write an operating system kernel, which means that our bootloader is running in a really harsh environment! Do you remember all libraries that we are lucky to have when developing normal software, well, none of them are available right now! And they will not be available until we decide to make them available and work to do that. Even the simple function "printf" of C is not available. 

But that's fine, for our luck, in this harsh environment, where there is too little available for us to write our code, BIOS provides us with a bunch of useful services that we can use in our bootloader to get things done. You can consider BIOS services as the APIs available on high-level languages that provide us with functions and classes to do what we want to do.

## Step 0: Creating Makefile

## Step 1: A bootloader that Prints "539kernel"
Let's start our journey and write a bootloader that prints the string "539kernel". 

We can call a BIOS service by using interrupts [^interrupts] and each service has its own unique number which receives unique parameters to perform some task. For example, BIOS has a service which has the number 12h [^hex], so to call this service in assembly code we use the instruction "int" which is short for interrupt.

```{.assembly}
int 12h
```

For now, you can consider the previous line as a call for a function named 12h which is provided by BIOS and performs some specific task. Well, to do our task of creating the bootloader that prints the string "539kernel" we are going to use the interrupt 10h, BIOS provides videos services through this interrupt. When we use interrupt 10h, we need to tell BIOS which video service we want to use, to do so, we need to set the value of the register *ah* to the service's number which we would like to use. The video service number *0Eh* prints one character on the screen. If we imagine interrupt 10h as a C function, it will have the following signature:

```{.c}
void interrupt_10( int ah /* Service Number */ )
```

So, you got the idea, when we want to pass a parameter to a BIOS service we need to use the registers. Each service specifies some specific registers to mean something special. As we have seen, interrupt 10h considers the register *ah* as the value holder of the required video service. In the same way, the printing service *0Eh* considers the register *al* as the holder of the character that we wish to print. One again, if we were in C world, it will be in this way:

```{.c}
void interrupt_10( int ah /* Service Number */, int al /* If the parameter ah == 0Eh, then this parameter should hold the character that we want to print */ )
```

Now, we are ready to write our first bootloader. 

## Historical Background 
IBM PC and BIOS

## Current Status
EFI

[^1]: Actually not any computer, but an IBM compatible computer.
[^2]: We will see later in this chapter that BIOS has been replaced by UEFI in modern computers.
[^3]: A magnetic hard disk has multiple stacked *platters*, each platter is divided into multiple *tracks* and inside each track there are multiple *sectors*. The size of a sector is 512 bytes, and from here the restricted size of a boot loader came.
[^real-mode]: We will see later what is the meaning of Real Mode in x86 architecture.
[^interrupts]: Another x86 concept. Don't worry, everything will be explained on its suitable time, just get the terms by faith right now.
[^hex]: Note "h" in the number, that means this number is in hexadecimal numbering system. It does't equal the decimal number 12. When we use hexadecimal number we use "h" as a postfix. For decimal numbers we use "d" as a postfix.