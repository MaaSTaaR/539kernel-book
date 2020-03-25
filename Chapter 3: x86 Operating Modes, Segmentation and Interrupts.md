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

The basic view of the main memory is that it is an *array of cells*, the size of each cell is a byte, each cell is able to store some data (of 1 bytes of course) and is reachable by a unique number called *memory address* ^[The architecture which each memory address points to `1 byte` is known as *byte-addressable architecture* or *byte machines*. It is the most common architecture, of course, other architectures are possible, such as *word-addressable architecture* or *word machines*.], the range of memory addresses starts from `0` until some limit, for example, if the system has `1MB` of *physical* main memory, then the last memory address in the range is `1023` ^[As we know, `1MB` = `1024 bytes` and since the range starts from `0` and not `1`, then the last memory address in this case is `1023` and not `1024`.]. This range of memory addresses is known as *address space* and we will see later that we can define a *logical* address space that differs from the *physical* address space ^[A well-known example of using logical address space is *virtual memory* that will be discussed in later chapter of this book.], when we say *physical* we mean the actual hardware, that is when the hardware of the main memory (RAM) size is `1MB` then the physical address space of the machine is up to `1MB`. On the other hand, when we say *logical* that means it doesn't necessarily represents or obeys the way the actual hardware works, instead it is a *logical* way of something that doesn't exist in the real world (the hardware), the differences between *logical* view and *physical* view is handled by the software or sometimes special parts of the hardware. An important example that we will discuss in later chapters is *virtual memory* which provides a logical address space of size `4GB` even if the actual size of physical main memory is less than `4GB`.

This view of memory, that is the *addressable array of bytes* can be considered as the physical view of the main memory which specifies the mechanism of accessing the data. Based on this physical view a logical view can be created and one example of logical view is *x86 segmentation*. In x86 segmentation the main memory is viewed as separated parts called *segments* and each segment stores some related data. Inside a segment, each byte can be referred to by its *offset*. The possible segments in x86 are: *code segment* which stores the code of the program under execution, *data segments* which store the data of the program and the *stack segment* which stores the data of program's stack. **[Figure shows the difference between segmentation view and the physical view .....]**

### Segmentation in Real Mode

We have said that logical views should be mapped to the physical view either by software or hardware, in this case, the segmentation view is realized and mapped to the architecture of the physical main memory by the x86 processor itself, that is, by the hardware. For this purpose, *segment registers* are presented in x86, the size of each segment register is `16-bit` and they are: `CS` which is used to define the code segment. `SS` which is used to define the stack segment. `DS`, `ES`, `FS` and `GS` which can be used to define data segments, that means each program can have up to four data segments. Each segment register stores the *starting memory address* of the segment ^[And here you can start to observe the mapping between the logical and physical view.].

<!--
### Segmentation in Protected Mode

The fundamentals of segmentation in protected mode is exactly same as the ones explained in real mode, but there are some differences which are presented in protected mode to provide more features such as *memory protection*. [The main difference is the meaning of a segment register's value]

## x86 Interrupts
-->

<!--
there is a way to switch from Real Mode to Protected Mode, but that's a story for a different day!
-->
