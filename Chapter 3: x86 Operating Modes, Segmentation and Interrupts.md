# x86 Operating Modes, Segmentation and Interrupts

## Introduction

In our situation, and by using modern terminology, we can view the processor as a *library* and *framework*, it provides us with a bunch of instructions to perform whatever we want, also it has general rules that organize the overall environment of execution, that is, it forces us to work in a specific way. We have seen some aspects of the first part when we have written the bootloader, that is, we have seen the processor as a library. In this chapter, we are going to see how the processor works as a framework by examining some important and basic concepts of x86. We need to understand these concepts to start the real work of writing 539kernel.

## x86 Operating Modes

In x86 an operating mode specifies the overall picture of the processor, such as how does it perform its tasks, the maximum size of available registers, the available advanced features for the running operating system and the restrictions.

When we developed the bootloader in the previous chapter we have worked with *x86 operating mode* named *real mode* ^[Its full name is *real address mode*.] which is an old operating mode which is still supported by modern x86 processors for the sake of backward compatibility and when the computer runs initially, it runs on real mode, for the same reason of backward compatibility.


Real mode is a 16-bit operating mode which means that, maximally, only 16-bit of register size can be used, even if the actual size of the registers is 64-bit ^[64-bit CPUs.]. Using only 16-bit of registers has consequences other than the size itself ^[These consequences are considered as disadvantages in modern days.] for example, in real mode the size of the main memory is limited, even if the computer has 16GB of memory, real mode can deal with only 1MB. Furthermore, any code which runs on real mode should be 16-bit code, for example, the aforementioned 32-bit registers (such as `eax`) cannot be used in real mode, their 16-bit counterparts should be used instead, for example, the 16-bit `ax` should be used instead of `eax` and so on.

Some core features of modern operating systems nowadays are multitaksing, memory protection and virtual memory ^[If some of these terms are new for you don't worry about them to much, you will learn them gradually through this book.] and real mode provides nothing to to implement these features. However, in modern x86 processors, new and more advanced operating modes have been introduction, namely, they are *protected mode* which is a 32-bit operating mode and *long mode* which is a relatively new 64-bit operating mode. Although the long mode provides more capacity for its users ^[For example, long mode can deal with 16 **exabytes** of memory.] we are going to focus on protected mode since it provides the same basic mechanisms that we need to develop a modern operating system kernel with the aforementioned features, hence, 539kernel is a 32-bit kernel which runs under protected mode.

As we have said, protected mode is a 32-bit operating mode, that is, registers with the size of 32-bit can be used, also, protected mode has the ability to deal with 4GB of main memory, and most importantly, it provides important features which we are going to explore through this book that helps us in implementing modern operating system kernel features.

## x86 Segmentation

The basic view of the main memory is that it is an *array of cells*, the size of each cell is a byte, each cell is able to store some data (of 1 bytes of course) and is reachable by a unique number called *memory address* ^[The architecture which each memory address points to `1 byte` is known as *byte-addressable architecture* or *byte machines*. It is the most common architecture, of course, other architectures are possible, such as *word-addressable architecture* or *word machines*.], the range of memory addresses starts from `0` until some limit, for example, if the system has `1MB` of *physical* main memory, then the last memory address in the range is `1023` ^[As we know, `1MB` = `1024 bytes` and since the range starts from `0` and not `1`, then the last memory address in this case is `1023` and not `1024`.]. This range of memory addresses is known as *address space* and it can be *physical address space* which is limited by the physical main memory or *logical address space*. An well-known example of using logical address space that we will be discuss in later chapters is *virtual memory* which provides a logical address space of size `4GB` even if the actual size of physical main memory is less than `4GB`.

When we say *physical* we mean the actual hardware, that is when the hardware of the main memory (RAM) size is `1MB` then the physical address space of the machine is up to `1MB`. On the other hand, when we say *logical* that means it doesn't necessarily represents or obeys the way the actual hardware works, instead it is a hypothetical way of something that doesn't exist in the real world (the hardware). To make the *logical* view of anything works, it should be mapped to the real *physical* view, that is, it should be somehow translated for the physical hardware, this mapping is handled by the software or sometimes special parts of the hardware.

This aforementioned view of memory, that is the *addressable array of bytes* can be considered as the physical view of the main memory which specifies the mechanism of accessing the data. Based on this physical view a logical view can be created and one example of logical views is *x86 segmentation*. In x86 segmentation the main memory is viewed as separated parts called *segments* and each segment stores a bunch of related data. To access data inside a segment, each byte can be referred to by its *offset*. The running program can be separated into three possible types of segments in x86. The types of x86 segments are: *code segment* which stores the code of the program under execution, *data segments* which store the data of the program and the *stack segment* which stores the data of program's stack. **[Figure shows the difference between segmentation view and the physical view .....]**

### Segmentation in Real Mode

For the sake of clarity, let's discuss segmentation under real mode first. We have said that logical views (of anything) should be mapped to the physical view either by software or hardware, in this case, the segmentation view is realized and mapped to the architecture of the physical main memory by the x86 processor itself, that is, by the hardware. So, for now we have a logical view, which is the concept of segmentation and dividing a program into separated segments, and the actual physical main memory view which is supported by the real RAM hardware and sees the data as a big array of bytes. Therefore, we need some tools to implement, that is mapping, the logical view of segmentation on top the actual hardware.

For this purpose, special registers named *segment registers* are presented in x86, the size of each segment register is `16-bit` and they are: `CS` which is used to define the code segment. `SS` which is used to define the stack segment. `DS`, `ES`, `FS` and `GS` which can be used to define data segments, that means each program can have up to four data segments. Each segment register stores the *starting memory address* of the segment ^[And here you can start to observe the mapping between the logical and physical view.]. In real mode, the size of each segment is `64KB` and as we have said we can reach any byte inside a segment by using the *offset* of the desired byte, you can see the resemble between a memory address of the basic view of memory and an offset of the segmentation view of memory ^[The concept and term of offset is not exclusive on segmentation, it is used on other topics related to the memory.]. Segmentation in x86 is unavoidable, the processor always runs with the mind that the running program is divided into segments.

Let's take an example to make the matter clear, assume that we have a code of some program loaded to the memory and its starting physical memory address is `100d`, that is, the first instruction of this program is stored in the address and the next instructions are stored right after this memory address one after another. To reach the first byte of this code we use the offset `0`, so, the whole physical address of the first byte will be `100:0d`, as you can see, the part before the colon is the starting memory address of the code and the part after the colon is the offset that we would like to reach and read the bytes inside it. In the same way, let's assume we would like to reach the offset `30`, which means the byte `33` inside the loaded code, them the physical address that we are trying to reach is actually `100:33d`. To make the processor handle this piece of code as the *current* code segment then its starting memory address should be loaded into the register `CS`.

As we have said, the x86 processor always runs with the mind that the segmentation is in use. So, let's say it is executing the following assembly instruction `jmp 150d` which jumps to the address `150d`. What really happens here is that to processor consider the value `150d` as an offset instead of a memory address, so, what the instruction requests for the processor here is to jump to the offset `150` which is inside the code segment, therefore, the processor is going to retrieve the value of the register `CS` to know what is the currently active code segment and append the value `150` to it. Say, the value of `CS` is `100`, then the memory address that the processor is going to jump to is `100:150d`. This is also applicable on the internal work for the processor, do you remember the register `IP` which is the instruction pointer? It actually stores the offset of the next instruction inside the code segment which is pointed to in the `CS` register. Any call (or jump) to a code inside the same code segment of the callee is known as *near call (or jump)*, otherwise is it a *far call (or jump)*. Again, let's assume the current value of `CS` is `100d` and you want to call a label which is on the memory location `9001d`, in this situation you are calling a code that reside in a different code segment, therefore, the processor is going to take the first part of the address `900d`, loads it to `CS` then load the offset `1d` in `IP`, because this call caused the changed of `CS` value to another value, it is a far call.

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

The fundamentals of segmentation in protected mode is exactly same as the ones explained in real mode, but it has been extended in protected mode to provide more features such as *memory protection*. In protected mode, a table named *global descriptor table* (GDT) is presented, this table is stored in the main memory and the starting memory address of it is stored in the special purpose register `GDTR`, each entry in this table called a *segment descriptor* which has the size `8 bytes` and they can be referred to by an index number called *segment selector* which is the offset of the entry from the starting memory address of GDT, that is, the content of the register `GDTR`, the first entry of GDT, which is entry #0, should not be used. An entry of GDT, that is, a segment descriptor, defines a segment and has the information that is required by the processor to deal with a segment, the starting memory address of the segment is stored in its descriptor ^[In real mode, the starting address of the segment is stored directly on the corresponding segment register (eg, `CS` for code segment).], also, the size (or limit) of the segment. The segment selector of the currently active segment should be stored in the corresponding segment register.

To clarify the matter, consider the following example. Let's assume we are running two programs currently and the code of each one of them is stored in the main memory and we would like to use each one of them as a separated code segment. Let's call them `A` which its starting memory address is `800` and `B` which is starting address is `900` and assume that the starting memory address of GDT is `500` and is already loaded in `GDTR`, to be able to use `A` and `B` as segments we should define a segment descriptor for each one of them. We already know that the size of a segment descriptor is `8 bytes`, so, if we define a segment descriptor for the segment `A` as entry #1 ^[Remember that the entries on GDT starts from zero.] then its offset in GDT will be `8`, the segment descriptor of `A` should have the starting address of `A` which is `800`, and we will define the segment descriptor of `B` as entry #2 which has the offset `16` since the previous entry took `8 bytes` from the memory, since the offset of `A`'s entry is `8` then its segment selector is also `8`, the same applies for `B`'s entry ^[And all other entries of course.] which its segment selector is `16`. Let's assume now that we want the processor to execute the code of segment `A`, we already know that the processor consults the register `CS` to know which code segment is currently active and should be executed next, for that, the **segment selector** of code segment `A` should be loaded in `CS`, so the processor can start executing it. In real mode, the content of `CS` and all other segment registers was a memory address, on the other hand, the content of `CS` and all other segment registers is a segment selector. In our situation, the processor takes the segment selector of `A` from `CS` which is `8` and the from the starting memory address of `GDTR` walks `8` bytes, so, if `GDTR = 500`, the processor will find the segment descriptor of `A` in the memory address `508`. The starting address of `A` will be found in the segment descriptor and the processor can use it with the value of register `EIP` to execute `A`'s code. Let's assume a far jump is occurred from `A` to `B`, then the value of `CS` will be changed to the segment selector of `B` which is `16`.

#### The Structure of Segment Descriptor

A segment descriptor is an `8 bytes` entry of global descriptor table which describes a specific segment in the memory. To be able to explain the structure of a segment descriptor in a simple way, let's handle it a series of `1 byte` fields starting from the byte `0` and ending in the byte `7`.

* Bytes `0` and `1`, that is, the first `16 bits` stores a **part** of segment segment's limit.
* Bytes `2`, `3` and `4` a part of segment's *base address* ^[The base address of the segment is its starting memory address.] is stored. 
* Byte `5` is divided into several components: 
	* The first `4 bits` ^[As the `8 bits` known as a byte, the `4 bits` is known as a *nibble*. That is, a nibble is a half byte.] known as *type field*.
	* The following bit is known as *descriptor type flag* (or *S flag*).
	* The following `2 bits` is known as *descriptor privilege level field* (DPL).
	* The last bit is known as *segment-present flag* (or *P flag*). 
* Byte `6` is also divided into several components
	* The first `4 bits` stores is the last part of segment limit.
	* The following bit is known as *AVL* and has no functionality, it is available for the operating system to use it however it wants.
	* The following bit is known as *L* and its value should always be `0` in 32-bit environment.
	* The following bit is known as *default operation size flag*.
	* The last bit is known as *granularity flag*.
* Byte `7` stores the last part of segment base address.

The segment limit and size are two different things, the limit can be used to infer the size of a segment, consider the following example to illustrate the matter.


<!--
#### The Special Register `GDTR`
#### Local Descriptor Table
-->


<!--
## x86 Interrupts
-->

<!--
there is a way to switch from Real Mode to Protected Mode, but that's a story for a different day!
-->
