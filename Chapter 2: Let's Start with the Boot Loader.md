# Let's Start with the Bootloader

## Introduction

When a computer powers on, a piece of code called bootloader is loaded and takes the control of the computer. Usually, the goal of the bootloader is loading the kernel of an operating system from the disk to the main memory and gives the kernel the control over the computer. The firmware of a computer is the program which loads the bootloader, in IBM-compatible computers the name of this program is BIOS (Basic Input/Output System).

There is a place in the hard disk called *boot sector*, it is the first sector of a hard disk ^[A magnetic hard disk has multiple stacked *platters*, each platter is divided into multiple *tracks* and inside each track there are multiple *sectors*. The size of a sector is 512 bytes, and from here the restricted size of a boot loader came.], BIOS is going to load the content of the boot sector as a first step of running the operating system. Loading the boot sector's content means that BIOS reads the content from hard disk and loads it into the main memory (RAM). This loaded content from the boot sector should be the bootloader, and once its loaded into the main memory, the CPU will be able to execute it as any normal application we use in our computers. So, the last step performed by BIOS in this process is giving the control to the bootloader to do whatever it wants.

So, before start writing 539kernel, we need to write the bootloader that is going to load 539kernel from the disk. In x86 architecture, the size of the bootloader is limited to 512 bytes and due to this restricted size and the need of using low-level services, the bootloader is usually written in assembly language, also, because of this restricted size, we cannot depend on BIOS to load 539kernel because it going to be larger that 512 bytes, The reason of this limited size of the bootloader is because of the size of a sector in the hard disk itself. Each sector in the hard disk has the size of 512 bytes and as we have mentioned, BIOS is going to load the content of the first sector of hard disk, the boot sector, which, of course, as any sector its size is 512 bytes.

The booting process is too specific to the computer architecture as we have seen and it may differs between one architecture and another. Some readers, especially Computer Science students may notice that the academic textbooks of operating systems don't mention the boot loader or discuss it.

## Hard Disk Structure

A hard disk consists of multiple *platters* which are stacked together one above the other, have you ever seen a CD or a DVD? A platter has exactly the same shape, refer to Figure @fig:a-platter. The both surfaces (top and down) of a platter are covered by a magnetic layer which stores the data. For each surface of a platter there is a read/write head on it, and as you guessed, the role of this head is to read from a surface or write to it, a head is attached to an arm. Those arms move horizontally, that is, back and forth, and because the other end of all of those arms are attached to the same physical part, they will be moved back and forth together to the same location at the same time. Figure @fig:platters-arms-heads shows how the platters, arms and read/write heads are assembled together.

![(A) Shows a platter when we see it from the side. (B) Shows a platter when we see it from top/down.](Figures/bootloader-ch/a-platter.png){#fig:a-platter width=50%}

A surface of a platter is divided into a number of tracks and each track is divided into a number of sectors. In Figure @fig:tracks-sectors you can see how tracks and sectors are organized on a surface, the gray circles that have the same center (cocenteric) are the tracks, a track consists of a smaller parts which called sectors.  A sector is the smallest unit that holds data in hard disks and as you know from our previous discussion, the first sector in a hard disk is the boot sector.

 ![Shows how the parts of a hard disk are assembled together.](Figures/bootloader-ch/platters-arms-heads.png){#fig:platters-arms-heads width=50%}

When the operating system needs to write some data to the hard disk or read from it, at least two mechanical moves ^[This fancy term "Mechanical Moves" means the physical parts of hard disk moves.] are performed. This first move is performed by the read/write arms, they move back or forth to be upon the track that contains the data we would like to read, this operation is known as *seek*. So, *seek time* is the time needed to put a specific track under read/write head. Until now, the read/write head is on the right track but also it is on a random sector ^[Not exactly random, can you tell why?], to reach the sector that we would like to read from (or write to) the platter rotates until the read/write head becomes on the desired sector. The speed of rotation is measured by the unit RPM (Revolutions Per Minute) and the needed time to reach the desired sector is known as *rotational latency*. Finally, the data will be *transferred* from the hard disk to the main memory, the time needed to transfer a number of bits known as *transfer time*.

Let's say that a hard disk has 3 platters, which means it has 6 surfaces, arms and read/write head. When the operating system request from the hard disk to seek a specific track, for instance track #3, all 6 heads will seek the track #3 and when the seek operation ends, the 6 heads will point to track #3 on all 6 surfaces, that is, the top head of the first platter and the bottom head of it is going to point to track #3, and so on for the other 4 remaining heads, the collection of all these tracks that the heads point to at some point of time is called a *cylinder*.

![Shows Tracks and Sectors on a platter's surface.](Figures/bootloader-ch/tracks-sectors.png){#fig:tracks-sectors width=50%}

Now, based on what we know about how a hard disk work, can we imagine what happens inside the hard disk when BIOS loads a bootloader? First, the arms will be *seek* the track number 0 ^[I didn't mention that previously, but yes, the bootloader resides in track #0.], that is, the arms move back or forth until they reach the track #0, then the platter rotates until the read/write head become upon the sector #0, finally, the content of sector #0 is transferred to the main memory.

## x86 Operating Mode
When the bootloader loads, it is going to work on *Real Mode* which is an x86 16-bit operating mode. Being a 16-bit operating mode means that only 16-bit of register size can be used, even if the actual size of the registers is 64-bit ^[64-bit CPUs.]. Using only 16-bit of registers has consequences other than the size itself, also, any code which is going to run on Real Mode should be 16-bit code, for example, the aforementioned 32-bit registers (such as `eax`) cannot be used in Real Mode, their 16-bit counterparts should be used instead, for example, the 16-bit `ax` should be used instead of `eax` and so on. 

Real Mode is old operating, and modern computers runs initially on this operating mode for backward compatibility. It has been replaced by modern operating modes: Protected Mode which is a 32-bit operating mode and Long Mode which is a 64-bit operating mode. One of Real Mode disadvantages is the limited size of main memory, even if the computer has 16GB of memory, Real Mode can deal with only 1MB. On the other hand, Protected Mode can deal with 4GB of memory. 539kernel is a 32-bit kernel, which means it is going to run on Protected Mode instead of Real Mode and there is a way to switch from Real Mode to Protected Mode, but that's a story for a different day! What we need to concern on now is creating a 16-bit bootloader that runs on Real Mode and loads the 32-bit 536kernel, it's fine for the bootloader to run on Real Mode instead of Protected Mode. After all, we don't need more than 1MB of main memory to run the bootloader.

## BIOS Services
We are trying to write an operating system kernel, which means that our bootloader is running in a really harsh environment! Do you remember all libraries that we are lucky to have when developing normal software (user-space software), well, none of them are available right now! And they will not be available until we decide to make them so and work hard to do that. Even the simple function `printf` of C is not available. 

But that's fine, for our luck, in this environment, where there is too little available for us to write our code, BIOS provides us with a bunch of useful services that we be can used in Real Mode, we can use these services in our bootloader to get things done. 

BIOS services are like a group of functions in high-level languages that is provided by some library, each function does something useful and we deal with those functions as black boxes, we don't know what's inside these functions but we know what they do and how to use them. So, basically, BIOS provides us a library and we are going to use some of these functions in our bootloader.

BIOS services are divided into categories, there are video services category, disk services category, keyboard services category and so on and each category is labeled by a number called *interrupt number*. In high-level world, we witnessed the same concept but with different mechanism, for example, C standard library provides us with many services (functions) such as input/output functions, string manipulation functions, mathematical functions and so on, these functions are categorized and each category is label by the *library name*, for example, all input/output functions can be found in `stdio.h` and so on. In BIOS, for example, the category of video services has the interrupt number 10h ^[ Note `h` in the number, that means this number is in hexadecimal numbering system. It does't equal the decimal number 10. When we use hexadecimal number we use `h` as a postfix.].

Inside each services category, these is a bunch of services, each one can do a specific thing. Also, there are labeled by a number. In C, a service is a function labeled by a name (printf for example) and this function reside in a library (stdio.h for example) which is same as a category of services in BIOS. As we said, the interrupt number 10h represents the category of video services, and the service of printing a character on a screen is represented by the number 0Eh.

Interrupts is a fundamental concept in x86 architecture. What we need to know about them right now is that they are a way to call a specific code which is registered to them and calling an interrupt in assembly is really simple:

```{.assembly}
int 10h
```

That's it! We use the instruction `int` and gives it the interrupt that we would like to call as an operand. In this example, we are calling the interrupt 10h which is, as we mentioned multiple time, the category of BIOS video services. When the CPU executes this instruction, BIOS will be called and based on the interrupt number it will know that we want to use one of available video services, but which one exactly!

In the previous example, we actually didn't tell BIOS which video service we would like to use and to do that we need to specify service number in `ah` register before calling the interrupt.

```{.assembly}
mov ah, 0Eh
int 10h
```

That's it, all the BIOS services can be used in this exact way. First we need to know what is the interrupt number that the service which we which to use belong to, then, we need to know the number of the service that we're going to use, we put the service number in the register `ah` then we call the interrupt by its number by using `int` instruction. The previous code calls the service of printing a character on a screen, but is it complete yet? Actually no, we didn't specify what is the character that we would like to print. We need something like parameters in high-level languages to pass additional information for BIOS to be able to do its job. Well, lucky us! the registers are here to the rescue.

When a BIOS service need additional information, that is, parameters. It expects to find these information in a specific register. For example, the service 0Eh in interrupt 10h expects to find the character that the user wants to print in the register `al`. So, the register `al` is one of service 0Eh parameter. The following code requests from BIOS to print the character S on the screen:

```{.assembly}
mov ah, 0Eh
mov al, 'S'
int 10h
```

## A Little Bit More of x86 Assembly
We need to learn a couple more things about x86 to be able to start. In NASM, each line in the source code has the following format.

```{.assembly}
label: instruction operands
```

The label is optional, the operands depend on x86 instruction in use, if it doesn't get any operand then we don't need to write any operand. To write comments on NASM we begin with semi-colon and write whatever we like after it as a comment, the rest of the source line will be considered as a part of the comment after writing the semi-colon.

A label is a way to give an instruction or a group of instructions a meaningful name, then we can use this name in other places in the source code to refer to this instruction/group of instructions, we can use labels for example to call this group of instructions or to get the starting memory address of these instructions. Sometimes, we may use labels to make the code more readable.

We can say that a label is something like the name of a function or variable in C, as we know a variable name in C is a meaningful name that represents the memory address of the place in the main memory that contains the value of a variable, the same holds for a function name. Labels in NASM works in the same way, underhood it represents a memory address. The colon in label is also optional.

```{.assembly}
print_character_S_with_BIOS:
    mov ah, 0Eh
    mov al, 'S'
    int 10h
```

You can see in the code above, we gave a meaningful name `print_character_S_with_BIOS` for the bunch of instructions that prints the character `S` on the screen. After defining this label in our source code, we can use it anywhere in the same source code to refer to this bunch of instructions.

```{.assembly}
call_video_service int 10h
```

This is another example of labels. This time we eliminated the optional colon in label's name and the label here point to only one instruction. Please not that extra whitespaces and new lines doesn't matter in NASM, so, the following is equivalent to the one above.

```{.assembly}
call_video_service
    int 10h
```

Consider the following code, what do you think it does?

```{.assembly}
print_character_S_with_BIOS:
    mov ah, 0Eh
    mov al, 'S'

call_video_service:
    int 10h
```

Still it prints `S` on the screen. Introducing labels in the source code doesn't change its flow, it will be executed sequentially whether we used the labels or not. The sequence of execution will not be changed by merely using labels, if we need to change the sequence of execution we need to use other methods than labels. You already know one of these methods which is calling an interrupt.

So, we can say that labels are more general than a variable name or function name in C. A label is a human-readable name for a memory location which can contain anything, code or data!

### Jump and Return Unconditionally

Let's start this section with a simple question. What happens when we call a function in C? Consider the following C code.

```{.c}
main()
{
    int result = sum( 5, 3 );

    printf( "%d\n", result );
}
```

Here, the function `main` called a function named `sum` here, this function reside in a different region in memory and by calling it we are telling the processor to go to this different region of memory and execute what's inside it, the function `sum` is going to do its job, and after that, in some magical way, the CPU is going to return to the original memory region where we called `sum` from and proceed the execution of the code that follows the calling of `sum`, in this case, the `printf` function. How does the CPU know where to return after completing the execution of `sum`?

The function which call another is named *caller* while the function which is called by the caller named *callee*, in the above C code, the caller is the function `main` while the callee is the function `sum`.

#### x86 Calling Convension

When a program is running, a copy of its machine code is loaded in the main memory, this machine code is a sequence of instructions which are understandable by the processor, these instructions are executed by the processor sequentially, that is, one after another in each cycle in the processor. So, when a processor starts a new *instruction cycle*, it fetches the next instruction that should be executed from the main memory and executes it ^[The instruction cycle is also called *fetch-decode-execute cycle*.]. Each *memory location* in the main memory is represented and referred to by a unique *memory address*, that means each instruction in the machine code of the program under execution has a unique memory address, consider the following hypothetical example of the memory addresses of each instruction in the previous C code, note that the memory addresses in this example are by no means accurate.

```{.c}
100 main() {
110    int result = sum( 5, 3 );
120    printf( "%d\n", result );
130 }

250 int sum( int firstNumber, int secondNumber ) {
260     return firstNumber + secondNumber;
270 }
```

So, the number on the left is the hypothetical memory address of the code line in the right, that means the function `main` starts from the memory address `100` and so on. Also, we can see that the callee `sum` resides in a far region of memory from the caller `main`.

*Program Counter* is a part of computer architecture which stores the *memory address* for the instruction that will be executed in the next instruction cycle of the processor. In x86, the program counter is a register known as *instruction pointer* and its name is `IP` in 16-bit and `EIP` in 32-bit.

When the above C code runs for the first time, the value of the instruction pointer will be `100`, that is, the memory address of the starting point of `main` function. When the instruction cycle starts it reads the value of the instruction pointer register `IP`/`EIP` which is `100`, it fetches the instruction which is stored in the memory location `100` and executes it ^[For the simplicity of explanation, the details of *decoding* have been eliminated.], then the memory address of the next instruction `110` will be stored in the instruction pointer register for the next instruction cycle. When the processor starts to execute the instruction of the memory location `110`, this time, the value of `IP`/`EIP` will be `250` instead of `120` because, you know, we are calling the function `sum` which resides in the memory location `250`. Each running program has a *stack* which is a region of memory ^[The stack as a region of memory (x86 stack) is not same as the *data structure* stack, the former implements the later.], we will examine later the *stack* in details but what is important for us now the following, when another function is called, in our case `sum`, the memory address of the next instruction of the callee `main` is *pushed* ^[Push means store something in a stack, this term is applicable for both x86 stack and the data structure stack, as we have said previously, x86 stack is an implementation of the stack data structure.] into the stack, so the memory address `120` will be pushed into the stack before calling `sum`, this address is called *return address*. Now, assume that the processor is executing the instruction in the memory location *270*, that is, finishing the execution of the callee `sum`, after the execution, the processor will find the return address which is `120` in the stack, get it and put it in the register `IP`/`EIP` for the next instruction cycle ^[External Reading: The is the cause of buffer overflow bugs.]. So, this is the answer of our original question in the previous section "How does the CPU know where to return after completing the execution of `sum`?".

#### The Instructions `call` and `ret`

The instruction `call` in assembly works exactly in the same way that we have explained in the previous section, it is used to call a code that resides in a given memory address, it is going to push the return address into the stack, and when the callee uses the instruction `ret` the return address from the stack is used to resume the execution of the caller. Consider the following example.

```{.assembly}
call print_character_S_with_BIOS
call print_character_S_with_BIOS

print_character_S_with_BIOS:
    mov ah, 0Eh
    mov al, 'S'
    int 10h
    ret
```

You can see here that we have used the code sample `print_character_S_with_BIOS` to define something like C function by using the instructions `call` and `ret`. It should be obvious that this code prints the character `S` two times.

### The One-Way Unconditional Jump with The Instruction "jmp"

<!--
### The Difference Between "call" and "jmp"
### Conditional Jump
### NASM's Pseudo-instructions

## Step 0: Creating Makefile

## Step 1: A bootloader that Prints "539kernel"
Let's start our journey and write a bootloader that prints the string "539kernel". 

We can call a BIOS service by using interrupts [^interrupts] and each service has its own unique number which receives unique parameters to perform some task. For example, BIOS has a service which has the number 12h, so to call this service in assembly code we use the instruction "int" which is short for interrupt.

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
-->
