# x86 Operating Modes, Segmentation and Interrupts

## Introduction

In our situation, and by using modern terminology, we can view the processor as a *library* and *framework*. A library because it provides us with a bunch of instructions to perform whatever we want, and a framework because it has general rules that organize the overall environment of execution, that is, it forces us to work in a specific way. We have seen some aspects of the first part when we have written the bootloader, that is, we have seen the processor as a library. In this chapter, we are going to see how the processor works as a framework by examining some important and basic concepts of x86. We need to understand these concepts to start the real work of writing 539kernel.

## x86 Operating Modes

In x86 an operating mode specifies the overall picture of the processor, such as how does it perform its tasks, the maximum size of available registers, the available advanced features for the running operating system and the restrictions.

When we developed the bootloader in the previous chapter we have worked with an *x86 operating mode* named *real mode* ^[Its full name is *real address mode*.] which is an old operating mode which is still supported by modern x86 processors for the sake of backward compatibility and when the computer turned on, it initially runs on real mode, for the same reason of backward compatibility.

Real mode is a 16-bit operating mode which means that, maximally, only 16-bit of register size can be used, even if the actual size of the registers is 64-bit ^[64-bit CPUs.]. Using only 16-bit of registers has consequences other than the size itself ^[These consequences are considered as disadvantages in modern days.] for example, in real mode the size of the main memory is limited, even if the computer has 16GB of memory, real mode can deal only with 1MB. Furthermore, any code which runs on real mode should be 16-bit code, for example, the aforementioned 32-bit registers (such as `eax`) cannot be used in real mode code, their 16-bit counterparts should be used instead, for example, the 16-bit `ax` should be used instead of `eax` and so on.

Some core features of modern operating systems nowadays are multitasking, memory protection and virtual memory ^[If some of these terms are new for you don't worry about them too much, you will learn them gradually throughout this book.] and real mode provides nothing to implement these features. However, in modern x86 processors, new and more advanced operating modes have been introduced, namely, *protected mode* which is a 32-bit operating mode and *long mode* which is a relatively new 64-bit operating mode. Although the long mode provides more capacity for its users ^[For example, long mode can deal with 16 **exabytes** of memory.] we are going to focus on protected mode since it provides the same basic mechanisms that we need to develop a modern operating system kernel with the aforementioned features, hence, 539kernel is a 32-bit kernel which runs under protected mode.

Since protected mode is a 32-bit operating mode then 32-bit of registers can be used, also, protected mode has the ability to deal with 4GB of main memory, and most importantly, it provides important features which we are going to explore through this book that helps us in implementing modern operating system kernel features. 

## Modern Operating Systems and the Need of Protection

As we have said before, *multitasking* is one of core features that modern operating systems provide. In multitasking environment more than one software can run at the same time ^[At least illusionary.] even if there is only one processor ^[Or the current processor has only one core.], for the sake of making our next discussion easier we should mention the term *process* which is used to describe a software which is currently running in a system, that is, a process is a running software. For example, if your web browser is currently running then this running instance of it is called a process, its code is loaded into the main memory and the processor is currently executing it. Another property of general-purpose operating systems that is allows the user to run any software from unknown sources which means these software cannot be trusted, they may contain code that intentionally or even unintentionally breach the security of the system or cause the system to crash. 

Due to these two properties of modern general-purpose operating systems, the system need to be protected from multiple actions. First, either in multitasking or monotasking ^[That is, only one process can run at a given time. DOS is a an example of monotask operating system.] environment the kernel of the operating system, which is the most sensitive part of the system, should be protected from current processes, no process should be able to access any part of the kernel's memory either by reading from it or writing to it, also, no process should be able to call any of kernel's code without kernel's consent. Second, in multitasking environment the running processes should be protected <!-- __HERE__: 17 Dec 2020 -->

To achieve this goal, the code of these running software are loaded into memory ^[You will find out later that this claim isn't too accurate. But for the sake of simplicity of explaination, consider that the code of **all** running software are loaded into the memory.], that means, one of these running software may access parts of memory that doesn't belong to itself. This behavior is undesirable of course, imagine that you have entered some sensitive information (e.g. credit card number) in one of a running software that you trust, and at the same time, without your knowledge, a malicious code which is a part of another running software is able to read the content of first software memory, it will be able to retrieve this sensitive information. Therefore, one of most important thing to be considered in multitasking environment is the matter of protection, the running software should not be trusted by the operating system, hence, it should protect the software from each other and also it should protect itself from the running software ^[Imagine that a running software can manipulate operating system data structures!].

Multiple features of x86 protected mode can be used to enforce protection in multiple aspects while running in multitasking environment, while we will explore memory protection ^[That is protecting the memory area of running software A from being accessed by software B.] later gradually, in this subsection we are going to focus our discussion on privilege levels.

<!-- __HERE__: 16 Dec 2020 -->

## The Basic View of Memory

The basic view of the main memory is that it is an *array of cells*, the size of each cell is a byte, each cell is able to store some data (of 1 bytes of course) and is reachable by a unique number called *memory address* ^[The architecture which each memory address points to `1 byte` is known as *byte-addressable architecture* or *byte machines*. It is the most common architecture, of course, other architectures are possible, such as *word-addressable architecture* or *word machines*.], the range of memory addresses starts from `0` to some limit `x`, for example, if the system has `1MB` of *physical* main memory, then the last memory address in the range is `1023` ^[As we know, `1MB` = `1024 bytes` and since the range starts from `0` and not `1`, then the last memory address in this case is `1023` and not `1024`.]. This range of memory addresses is known as *address space* and it can be *physical address space* which is limited by the physical main memory or *logical address space*. A well-known example of using logical address space that we will be discuss in later chapters is *virtual memory* which provides a logical address space of size `4GB` in 32-bit architecture even if the actual size of physical main memory is less than `4GB`. However, The address space starts from the memory address `0`, which is the index of the first cell (byte) of the memory, and it increases by `1`, so the memory address `1` is the index of the second cell of the memory, `2` is the index of third cell of memory and so on.

When we say *physical* we mean the actual hardware, that is when the hardware of the main memory (RAM) size is `1MB` then the physical address space of the machine is up to `1MB`. On the other hand, when we say *logical* that means it doesn't necessarily represents or obeys the way the actual hardware works, instead it is a hypothetical way of something that doesn't exist in the real world (the hardware). To make the *logical* view of anything works, it should be mapped into the real *physical* view, that is, it should be somehow translated for the physical hardware, this mapping is handled by the software or sometimes special parts of the hardware.

Now, for the following discussion, let me remind you that the memory address is just a numerical value, it is just a number. When I discuss the memory address as a mere number I call it *memory address value* or *the value of memory address*, while the term *memory address* keeps its meaning, which is a unique identifier that refers to a specific location (cell) in the main memory.

The values of memory addresses are used by the processor all the time to perform its job, and when it is executing some instructions that involve the main memory (e.g. reading a content from some memory location), the related values of memory addresses are stored temporarily on the registers of the processor, due to that, the length of a memory address value is bounded to the size of the processor's registers, so, in `32-bit` environments, where the size of the registers is usually `32-bit`, the length of the memory address value is **always** `32 bits`, Why am I stressing "always" here? because even if less than `32 bits` it is enough to represent the memory address value, it will be represented in `32 bits` though, for example, assume the memory address value `1`, in binary, the value `1` can be represented by only `1 bit` and no more, by in reality, when it is stored (and handled) by the `32-bit` processor, it will be stored as the following sequence of bits

```{.c}
00000000 00000000 00000000 00000001
```

As you can see, the value `1` has been represented in exactly `32 bits`, appending zeros to the left doesn't change the value itself, it is similar to writing a number as `0000539` which is exactly `539`. The processor works with all values, beside the memory addresses values, as a sequence of *binary number*. It is natural for us as human beings to deal with numbers as *decimal numbers*.

A number by itself is an abstract concept, it is something in our mind, but to communicate with each others, we represent the numbers by using symbols which is named *numerals*. For example, the conceptual number one can be represented by different *numeral systems*. In Arabic numeral system the number one is expressed as `1`, while Roman numeral system it is expressed as `I`. A numeral system is *writing system*, that is, it gives us rules to write a number down as a symbol, it focuses on the way of writing the numbers. On the other hand, the numbers can be dealt with by a *numbering system*, we use the *decimal numbering system* to deal with numbers, think about them and perform arithmetic operations upon them, the processor use the *binary numbering system* to do the same with numbers. There are numbering systems other that the decimal and binary numbering system, and any number can be represented by any numbering system.

A number system is defined by its *base* which is also called *radix*, this base defines the list of available *digits* in the numbering system starting from `0` to `base - 1`, and the total of available digits equals the base. Consider the decimal numbering system, its base is `10` which means the available digits are: `0, 1, 2, 3, 4, 5, 6, 7, 8, 9`, a total of `10` digits. These digits can be used to create larger numbers, for example, `539` which consists of the digits `5`, `3` and `9`.

On the other hand, the base of binary numbering system is `2`, therefore, the available digits are only `0` and `1`, and as in the decimal numbering system they can be used to compose larger numbers, for example, the number `two` in binary numbering system is `10` ^[And from here came the well-known joke: "There are 10 types of people in this world, those who understand binary and those who don't".], be careful, this numeral does not represent the number `ten`, it represents the number `two` but in binary numbering system. When we discuss numbers in different numbering systems, we put the initial letter of the numbering system name in the last of the number, for example, `10d` and `10b` are two different numbers, the first one is `ten` in **d**ecimal which the second one is `two` in **b**inary.

Furthermore, basic arithmetic operations such as addition and subtraction can be performed on the numbering system, for example, in binary `1 + 1 = 10` and it can be performed systematically, also, a representation of any number in any numbering system can be converted to any other numbering system systematically ^[I think It's too brave to state this claim, however, it holds at least for the well-known numbering system.], while this is not a good place to show how to perform the operations and conversions for different numbering system, I have dedicated Appendix A for this sake.

By now it should be obvious for you that changing the base (radix) gives us a new numbering system and the base can be any number ^[Which implies that the total of numbering systems is infinite!], one of useful and well-known numbering system is *hexadecimal* which its base is `16` and its digits are `0, 1, 2, 3, 4, 5, 6, 7, 8, 9, A, B, C, D, E, F` where `A` means `ten`, `B` means `eleven` and so on. So, why hexadecimal is useful in our situation? We know binary is used in the processor and it is easier for us to discuss some entities such as the memory addresses in binary instead of decimal due to that, but have you seen the previous example of memory address value in binary?

```{.asm}
00000000 00000000 00000000 00000001b
```

It is too long and it will be tedious to work with, and for that the hexadecimal numbering system come be useful. Each digit in hexadecimal represents **four** bits ^[Can you tell why? [Hint: How the maximum hexadecimal number `F` is represented in binary?]], that is, the number `0h` in **h**exadecimal is equivalent to `0000b` in binary. As the `8 bits` known as a byte, the `4 bits` is known as a *nibble*, that is, a nibble is a half byte. And, as we have said, but in other words, one digit of hexadecimal represents a nibble. So, we can use hexadecimal to represent the same memory address value in more elegant way.

```{.asm}
00 00 00 01h
```

<!-- 
TODO: [TABLE OF NUMBER REPRESENTATIONS IN THE DIFFERENT NUMBERING SYSTEMS]** 
-->

From our previous discussions you may glanced that the register size that stores the values of memory address in the processor in order to deal with memory contents affects the available size of main memory for the system. Take for example the instruction pointer register, if its size say `16 bits` then the maximum available memory will be `64KB` ^[64 KB = 65536 Bytes / 1024], and if its size is `32 bits`, then the maximum available memory will be `4GB`. Why is that? To answer this example let's work with decimal numbers first. If I tell you that you have five blanks, what is the largest decimal number you can represent in these five blanks? the answer is `99999d`. In the same manner, if you have 5 blanks, what is the largest binary number you can represent in these 5 blanks? it is `11111b` which is equivalent to `31d`, the same holds for the registers that store the value of memory addresses, given the size of such register is `16 bits`, then there is 16 blanks, and the largest binary number that can be represented in those 16 blanks is `11111111 11111111b` or in hexadecimal `FF FFh`, which is equivalent to `65535d`, that means the last bytes a register of size `16 bits` can refer to is the byte number `65535d` because it is the largest value this register can store and no more, which leads to the maximum size of main memory this register can handle, it is `65535 bytes` which is equivalent to `64KB`.


## x86 Segmentation

The aforementioned view of memory, that is the *addressable array of bytes* can be considered as the *physical* view of the main memory which specifies the mechanism of accessing the data. On top of this physical view a *logical* view can be created and one example of logical views is *x86 segmentation*. 

In x86 segmentation the main memory is viewed as separated parts called *segments* and each segment stores a bunch of related data. To access data inside a segment, each byte can be referred to by its *offset*. The running program can be separated into three possible types of segments in x86. The types of x86 segments are: *code segment* which stores the code of the program under execution, *data segments* which store the data of the program and the *stack segment* which stores the data of program's stack.

<!-- TODO[FIGURE]
**[Figure shows the difference between segmentation view and the physical view .....]** -->

### Segmentation in Real Mode

For the sake of clarity, let's discuss segmentation under real mode first. We have said that logical views (of anything) should be mapped to the physical view either by software or hardware, in this case, the segmentation view is realized and mapped to the architecture of the physical main memory by the x86 processor itself, that is, by the hardware. So, for now we have a logical view, which is the concept of segmentation and dividing a program into separated segments, and the actual physical main memory view which is supported by the real RAM hardware and sees the data as a big array of bytes. Therefore, we need some tools to implement, that is mapping, the logical view of segmentation on top the actual hardware.

For this purpose, special registers named *segment registers* are presented in x86, the size of each segment register is `16-bit` and they are: `CS` which is used to define the code segment. `SS` which is used to define the stack segment. `DS`, `ES`, `FS` and `GS` which can be used to define data segments, that means each program can have up to four data segments. Each segment register stores the *starting memory address* of the segment ^[And here you can start to observe the mapping between the logical and physical view.]. In real mode, the size of each segment is `64KB` and as we have said we can reach any byte inside a segment by using the *offset* of the desired byte, you can see the resemblance between a memory address of the basic view of memory and an offset of the segmentation view of memory ^[The concept and term of offset is not exclusive on segmentation, it is used on other topics related to the memory.]. Segmentation in x86 is unavoidable, the processor always runs with the mind that the running program is divided into segments.

Let's take an example to make the matter clear, assume that we have a code of some program loaded to the memory and its starting physical memory address is `100d`, that is, the first instruction of this program is stored in this address and the next instructions are stored right after this memory address one after another. To reach the first byte of this code we use the offset `0`, so, the whole physical address of the first byte will be `100:0d`, as you can see, the part before the colon is the starting memory address of the code and the part after the colon is the offset that we would like to reach and read the bytes inside it. In the same way, let's assume we would like to reach the offset `33`, which means the byte `33` inside the loaded code, them the physical address that we are trying to reach is actually `100:33d`. To make the processor handle this piece of code as the *current* code segment then its starting memory address should be loaded into the register `CS`.

As we have said, the x86 processor always runs with the mind that the segmentation is in use. So, let's say it is executing the following assembly instruction `jmp 150d` which jumps to the address `150d`. What really happens here is that the processor consider the value `150d` as an offset instead of a memory address, so, what the instruction requests from the processor here is to jump to the offset `150` which is inside the *current* code segment, therefore, the processor is going to retrieve the value of the register `CS` to know what is the currently active code segment and append the value `150` to it. Say, the value of `CS` is `100`, then the memory address that the processor is going to jump to is `100:150d`. 

This is also applicable on the internal work for the processor, do you remember the register `IP` which is the instruction pointer? It actually stores the offset of the next instruction inside the code segment which is pointed to in the `CS` register instead of the whole memory address of the instruction. Any call (or jump) to a code inside the same code segment of the caller is known as *near call (or jump)*, otherwise is it a *far call (or jump)*. Again, let's assume the current value of `CS` is `100d` and you want to call a label which is on the memory location `9001d`, in this situation you are calling a code that reside in a different code segment, therefore, the processor is going to take the first part of the address which is`900d`, loads it to `CS` then loads the offset `1d` in `IP`. Because this call caused the changed of `CS` value to another value, it is a far call.

The same is exactly applicable to the other two types of segments and of course the  instructions deal with different segments based on their functionality, for example, you have seen that `jmp` and `call` both the with the code segment in `CS`, while the instruction `lodsb` deals with the data segment `DS`, the instruction `push` deals with the stack segment `SS` and so on.

In the previous chapter, when we wrote the bootloader, we have dealt with the segments. Let's go back to the source code of the bootloader, you remember that the firmware loads the bootloader on the memory location `07C0h` and because of that we started our bootloader with the following lines.

```{.asm}
	mov ax, 07C0h
	mov ds, ax
```

Here, we told the processor that the data segment of our program (the bootloader) starts in the memory address `07C0h` ^[Yes, all segments can be on the same memory location, that is, there is a `64KB` segment of memory which is considered as the currently active code segment, data segment and stack segment. This type of design is known as *flat-memory model* and we will discuss it later on.], so, if we refer to the memory to read or write and *data*, start with the memory address `07C0h` and then append the offset that we are referring to. The second use of the segments in the bootloader is when we tried to load the kernel from the disk by using the BIOS service `02h:13h` in the following code.

```{.asm}
	mov ax, 1000h
	mov es, ax
	
	mov ah, 02h
	mov al, 01h
	mov ch, 0h
	mov cl, 02h
	mov dh, 0h
	mov dl, 80h
	mov bx, 0h
	int 13h
```

You can see here, we have used the other data segment `ES` here and defined a new segment that starts from the memory address `1000h`, we did that because the BIOS service `02h:13h` loads the desired content (in our case the kernel) to the memory address `ES:BX`, for that, we have defined the new data segment and set the value of `bx` to `0h`. That means the code of the kernel will be loaded on `1000:0000h` by `02h:13h` and because of that, after loading the kernel successfully we have performed a far jump.

```{.asm}
jmp 1000h:0000
```

Once this instruction is executed, the value of `CS` will be changed from the value `07C0h` where the bootloader reside to the value `1000h` where the kernel is reside and the execution of the kernel is going to start.

### Segmentation in Protected Mode

The fundamentals of segmentation in protected mode is exactly same as the ones explained in real mode, but it has been extended to provide more features such as *memory protection*. In protected mode, a table named *global descriptor table* (GDT) is presented, this table is stored in the main memory and its starting memory address is stored in the special purpose register `GDTR`, each entry in this table called a *segment descriptor* which has the size `8 bytes` and they can be referred to by an index number called *segment selector* which is the offset of the entry from the starting memory address of GDT, that is, the content of the register `GDTR`, the first entry of GDT, which is entry #0, should not be used. An entry of GDT, that is, a segment descriptor, defines a segment (of any type) and has the information that is required by the processor to deal with a segment, the starting memory address of the segment is stored in its descriptor ^[In real mode, the starting address of the segment is stored directly on the corresponding segment register (eg, `CS` for code segment).], also, the size (or limit) of the segment. The segment selector of the currently active segment should be stored in the corresponding segment register.

<!-- TODO: Comparison between C array terms and GDT terms to make it clearer and more memorable for the reader. -->

To clarify the matter, consider the following example. Let's assume we are running two programs currently and the code of each one of them is stored in the main memory and we would like to use each one of them as a separated code segment. Let's call them `A` which its starting memory address is `800` and `B` which is starting address is `900` and assume that the starting memory address of GDT is `500` and is already loaded in `GDTR`, to be able to use `A` and `B` as segments we should define a segment descriptor for each one of them. We already know that the size of a segment descriptor is `8 bytes`, so, if we define a segment descriptor for the segment `A` as entry #1 ^[Remember that the entries on GDT starts from zero.] then its offset in GDT will be `8`, the segment descriptor of `A` should have the starting address of `A` which is `800`, and we will define the segment descriptor of `B` as entry #2 which has the offset `16` since the previous entry took `8 bytes` from the memory<!--, since the offset of `A`'s entry is `8` then its segment selector is also `8`, the same applies for `B`'s entry ^[And all other entries of course.] which its segment selector is `16`. [NOTE] I think this is a mistake. Need to recheck.--> Let's assume now that we want the processor to execute the code of segment `A`, we already know that the processor consults the register `CS` to know which code segment is currently active and should be executed next, for that, the **segment selector** of code segment `A` should be loaded in `CS`, so the processor can start executing it. In real mode, the value of `CS` and all other segment registers was a memory address, on the other hand, in protected mode, the value of `CS` and all other segment registers is a segment selector. In our situation, the processor takes the segment selector of `A` from `CS` which is `8` and the from the starting memory address of `GDTR` walks `8` bytes, so, if `GDTR = 500`, the processor will find the segment descriptor of `A` in the memory address `508`. The starting address of `A` will be found in the segment descriptor and the processor can use it with the value of register `EIP` to execute `A`'s code. Let's assume a far jump is occurred from `A` to `B`, then the value of `CS` will be changed to the segment selector of `B` which is `16`.

<!-- 10 July 2020. TODO: We need to say that with each reference to the memory, x86 is going to refer to GDT in order to protect the separated segments and get necessary information. -->

#### The Structure of Segment Descriptor

A segment descriptor is an `8 bytes` entry of global descriptor table which stores multiple *fields* and *flags* that describe the properties of a specific segment in the memory. With each memory reference by the running code to a segment, the processor is going to consult the descriptor that describes the segment in question to obtain basic information like starting memory address of this segment, also, segmentation in x86 is considered as a way for *memory protection*, a descriptor stores the properties of memory protection. By using those stored properties the processor will be able to protect the different segments on the system from each other and not letting some less privileged to call a code or manipulate data which belong to more privileged area of the system, a concrete example of that is when a userspace software (e.g. Web Browser) tries to modify an internal data structure in the kernel . In the following, the explanation of each field and flag of segment descriptor, but before getting started we need to note that here and in Intel's official x86 manual the term *field* is used when the information the field represents occupies **more than** `1 bit` from the descriptor, for example the segment's starting memory address is stored in `4 bytes`, then the place where this address is stored in the descriptor is called a field, otherwise the term *flag* is used, which means that the information which is stored in the flag occupies only `1 bit`.

##### Segment's Base Address and Limit
The most important information about a segment is its starting memory address, which is called the *base address* of a segment. In real mode, the base address was stored in the corresponding segment register directly, but in protected mode, where we have more information about a segment than mere base address, then this information will be stored in the descriptor of the segment ^[Reminder: In protected mode, the corresponding segment register stores the selector of the currently active segment.].

When the currently running code refers to a memory address to read from it, write to it (in the case of data segments) or call it (in the case of code segments) it is actually referring to a specific segment in the system ^[And it **should** since segmentation is enabled by default in x86 and cannot be disabled.]. For the simplicity of next discussions, we call this memory address (which is referenced by the currently running code) the *generated memory address* because, you know, it is generated by the code.

Any generated memory address in x86 architecture is not an actual physical memory address ^[Remember our discussion of the difference between our logical view of the memory (e.g. segmentation) and the actual physical hardware], that means, if you hypothetically get a generated memory address and try to get the content of its physical memory location, the obtained data will not be same as the data which is required by the code. Instead, a generated memory address is called by Intel's official manual a *logical memory address* because, you know, it is not real memory address, **it is** logical. Every logical memory address refers to some byte in a specific segment in the system, and to be able to obtain the data from the actual physical memory, this logical memory address should be *translated* to a *physical memory address* ^[We can see here how obvious the mapping between the logical view of the memory and the real-world memory.].

The logical memory address may pass **two** translation processes to obtain the physical memory address instead of one. The first address translation is performed on a logical memory address to obtain a *linear memory address* ^[Which is another not-real and not physical memory address which is there in x86 architecture because of paging feature.], if paging ^[Don't worry about paging right now. It will be discussed later in this book. All you need to know now is that paging is another logical view of the memory.] is enabled ^[It is disabled by default which makes paging an optional feature in x86, unlike segmentation.] in the system, a second translation process takes place om this linear memory address to obtain the real physical memory address. If paging is disabled, the linear memory address which is generated by the first translation process is same as the physical memory address. We can say that the first translation is there in x86 due to the segmentation view of memory, while the second translation is there in x86 due to the paging view of memory.

<!-- [MQH] 11 July 2020. TODO[FIGURE] The process of translation a logical memory address and the last result when paging is enabled or disabled -->

Hence, for now, our focus will be on the translation from a logical memory address to a linear memory address and this memory address, which is the output of the translation process, is same as the physical memory address since paging feature is disabled by default in x86. As we have said before, any reference to a memory address by the running code means that some specific segment is referred and the running code need to obtain (or call) some data inside this specific segment, due to that, the logical memory address and its translation is in fact all about segmentation.

Each logical memory address consists of two parts, a `16-bit` segment selector and a `32-bit` offset. When the currently running code generate a logical memory address, for instance, to read some data from memory, the processor need to perform the translation process to obtain the physical memory address. First, it reads the value of the register `GDTR` which contains the starting physical memory address of GDT, then it uses the `16-bit` segment selector in the generated logical address to locate the descriptor of the segment that the code would like to read the data from, inside segment's descriptor, the physical base address (the starting physical address) of the requested segment can be found, the processor obtains this base address and adds the `32-bit` offset from the logical memory address to the base address to obtain the last result, which is the linear memory address.

<!-- [MQH] 11 July 2020. TODO[FIGURE] the process of translating logical memory address to linear memory address. -->

During this operation, the processor uses the other information in the segment descriptor to enforce the policies of memory protection. One of these policies is defined by the *limit* of a segment which specifies its size, if the generated code refers to an offset which exceeds the limit of the segment, the processor should stop this operation. For example, assume hypothetically that the running code has the privilege to read data from data segment `A` and in the physical memory another data segment `B` is defined right after the limit of `A`, which means the offset `limit + 1` reaches to the first byte of `B` which is a critical data segment which stores kernel's internal data structures and we don't want any code to read from it or write to it if it is not privileged. This can be achieved by specifying the limit of `A` correctly, and when the unprivileged tries maliciously to read from `B` be generating a logical memory address that has an offset which exceeds the limit of `A` the process is going to prevent the operation and protect the content of segment `B`. Segment's limit is not the only feature which is provided by x86 segmentation for memory protection, we will see more in the next subsections.

Back to the structure of descriptor, the bytes `2`, `3` and `4` of the descriptor store the *least significant bytes* of segments base address and the by `7` of the descriptor store the *most significant byte* of the base address, that's `32-bit` for the base address. While the bytes `0` and `1` of the descriptor store the *least significant bytes* of segment's limit and byte `6` stores the *most significant byte* of the limit.

Before finishing this subsection, we need to define the meaning of *least significant* and *most significant* byte or bit. Take for example the following binary sequence which may represent anything, from a memory address value to a UTF-32 character.

**0**111 0101 0000 0000 0000 0000 0100 110*1*

You can see the first bit from left is on bold format and its value is `0`, based on its position in the sequence we call this bit the *most significant bit* or *high-order bit*, while the last bit on the right which is on italic format and its value is `1` is known as *least significant bit* or *low-order bit*. The same terms can be used on byte level, given the same sequence with different formatting.

**0111 0101** 0000 0000 0000 0000 *0100 1101*

The first byte (`8-bits`) on the left which is on bold format and its value is `0111 0101` is known as *most significant byte* or *high-order byte* while the last byte on the right which is on italic format and its value is `0100 1101` is known as *least significant byte* or *low-order byte*.

Now, imagine that this binary sequence is the base address of a segment, then the least significant `3` bytes of it will be stored in bytes `2`, `3` and `4` of the descriptor, that is, the following binary sequence.

```{.asm}
0000 0000 0000 0000 0100 1101
```

While the most significant byte of the binary sequence will be stored in the `7th` byte of the descriptor, that is, the following binary sequence.

```{.asm}
0111 0101
```

##### Segment's Type
Given any binary sequence, it doesn't have any meaning until some context is added. For example, what does the binary sequence `1100 1111 0000 1010` represents? It could represent anything, a number, characters, pixels on image or even all of them based on how its user interprets it. When an agent (e.g. a bunch of code in running software or the processor) works with a binary sequence, it should know what does this binary sequence represent to be able to perform useful tasks. In the same manner, when a segment is defined, the processor (the agent) should be told how to interpret the content inside this segment, that is, the type of the segment should be known by the processor.

Till this point, you probably noticed that there is at least two types of segments, code segment and data segment. The content of the former should be machine code that can be executed by the processor to perform some tasks, while the content of the latter should be data (e.g. values of constants) that can be used by a running code. These two types of segment (code and data) belong to the category of *application segments*, there is another category of segment types which is the category of *system segments* and it has many different segment types belong to it.

Whether a specific segment is an application or system segment, this should be mentioned in the descriptor of the segment in a flag called *S flag* or *descriptor type flag* which is the fifth **bit** in **byte** number `5` of the segment descriptor. When the value of S flag is `0`, then the segment which is described by the descriptor is considered as a system segment, while it is considered as an application segment when the value of S flag is `1`. Our current focus is on the latter case.

As we have mentioned before, an application segment can be either code or data segment. Let's assume some application segment has been referenced by a currently running code, the processor is going to consult the descriptor of this segment, and by reading the value of S flag (which should be `1`) it will know that the segment in question is an application segment, but which of the two types? Is it a code segment or data segment? To answer this question for the processor, this information should be stored in a field called *type field* in the segment's descriptor.

Type field in segment descriptor is the first `4-bits` (nibble) of the fifth byte of the descriptor and the most significant bit specifies if the application segment is a code segment (when the value of the bit is `1`) or a data segment (when the value of the bit is `0`). Whether the segment is a code or data segment, the least significant bit indicates if the segment is *accessed* or not, when the value of this flag is `1`, that means the segment has been written to or read from (AKA: accessed), but if the value of this flag is `0`, that means the segment has not been accessed. The value of this flag is manipulated by the processor in one situation only, and that's happen when the selector of the segment in question is loaded into a segment register. In any other situation, it is up to the operating system to decide the value of accessed flag. According to Intel's manual, this flag can be used for virtual memory management and for debugging.

###### Code Segment Flags
When the segment is a code segment, the second most significant bit (tenth bit) called *conforming flag* ^[AKA: `C` flag.] while the third most significant bit (ninth bit) called *read-enabled flag* ^[AKA: `R` flag.]. Let's start our discussion with the simplest among those two flags which is the read-enabled flag, which its value indicates how the code inside the segment in question can be used, when the value of read-enabled flag is `1` ^[Which means **do** enable read since `1` is equivilant to `true` in the context of flags.], that means the content of the code segment can be executed **and** read from, but when the value of this flag is `0` ^[Which means **don't** enable read.] that means the content of the code segment can be **only** executed and cannot read from. The former option can be useful when the code contains data inside it (e.g. constants) and we would like to provide the ability of reading this data. When read is enabled for the segment in question, the selector of this segment can also be loaded into one of data segment register ^[Which makes sense, enabling reads from a code segment means it contains data also.].

The conforming flag is related to the privilege levels that we had an overview about them previously in this chapter.

<!-- [MQH] 23 Oct 2020. WE ARE HERE. Go to "x86 Operating Modes" section and write an overview about privilege levels (Big Picture) to be able to explain the purpose of "conforming flag". Note: use high-level terms in here such as "less-privileged" and "more-privileged" instead of the technical ones such as "CPL" and "DPL", there will be a section below for those stuff. -->

###### Data Segment Flags
When the segment is data segment, the second most significant bit (tenth bit) called `E` flag while the third most significant bit (ninth bit) called `W` flag.




<!--
* Byte `5` is divided into several components: 
	* The first `4 bits` known as *type field*.
	* The following bit is known as *descriptor type flag* (or *S flag*).
	* The following `2 bits` is known as *descriptor privilege level field* (DPL).
	* The last bit is known as *segment-present flag* (or *P flag*).
-->

<!--
##### Granularity Flag 

##### Other Fields and Flags
-->
<!--
* Byte `6` is also divided into several components
	* The first `4 bits` stores is the last part of segment limit.
	* The following bit is known as *AVL* and has no functionality, it is available for the operating system to use it however it wants.
	* The following bit is known as *L* and its value should always be `0` in 32-bit environment.
	* The following bit is known as *default operation size flag*.
	* The last bit is known as *granularity flag*.
-->

<!--
#### The Technical Details of Privilege Levels
#### The Special Register `GDTR`
#### Local Descriptor Table
-->

<!--
TODO [10 July 2020]: Final word about segmentation: after all of these complex details, you should not forget the simple purpose of it. [Review the concept for the reader]
-->


<!--
## x86 Interrupts
-->