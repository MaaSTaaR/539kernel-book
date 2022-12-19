---
title:  'A Journey in Creating an Operating System Kernel: The 539kernel Book'
author: 'Mohammed Q. Hussain'
---

# Chapter 4: Process Management {#ch-process-management}

## Introduction
In the previous chapters, we have discussed the topics that helped us understand the basics that are needed to initialize the environment for a `32-bit` protected mode kernel running on x86. Starting from this chapter we are going to discuss the topics that belong to the kernel itself, that is, the responsibilities of the kernel. We will start with a quick look at the theories that are traditionally presented in academic textbooks, then we move to the practical part in order to implement these theories (or part of them) in the 539kernel. A good place to start from is *process management*.

A kernel has multiple responsibilities, one of these responsibilities is to manage the resources and make sure they are managed well. One important resource of a computer is the time spent utilizing the processor (AKA: CPU time) which is the component that executes the code of software that we would like to run on our machines. Process management is the part is concerned with how a kernel should manage and distribute CPU time among a bunch of *processes*.

## The Most Basic Work Unit: A Process
*Process* is the term which is used in operating systems literature to describe a running program. In the previous chapters of this book we have encountered the concept of a process multiple times and you may recall from these encounters that every user-space program that we use in our computers is represented by a soulless sequence of bytes that are stored somewhere on the hard disk. When we decide to use a specific program, for example, the web browser, the first thing we do is to open it either through double clicking on its icon in the graphical user interface or through writing its command in the shell. When we do that, the kernel is called through a *system call* and takes the responsibility of "opening" this program. We can view system calls as functions which are provided by the kernel to expose its services for the user-space software. One way of implementing system calls is to use interrupts, exactly the same way as we have used with the BIOS.

However, there are several steps that are needed to be performed to open the program, for example, reading its data from disk, but our current focus is on the parts related to process management. Eventually, the kernel creates a new process for the program that we requested to open. The kernel maintains a table of all processes in the system, each entry represents a process and contains the information which is needed by the kernel to manage the process. The data structure which stores the process information is known as the *process control block* (PCB), so, the process table will have a process control block entry for each process in the system.

Of course, the most important parts of a process are the program code and its data. Both, code and data [^1], should be loaded into memory, after that, the code of a process can be executed by the processor. We need to note that a process is an instance of a program, in other words, one program can be opened multiple times each time creating a separate process. For example, when opening multiple windows of the web browser at the same time, there is just one program, the web browser, which is represented by the binary file stored on the hard disk, but each opened window is a separate process and each process' contents are stored in the main memory separately from the other process' contents even if they are instances of the same program. While the described concept is well-known by the term "process", especially in the literature, other terms can be used for the same concept, for example *task* and *job* are other words which are used to describe the same concept.

Each process is known to have a *state*, when it is loaded to the memory its state will be indicated by the kernel as *ready*. This means that the process is ready run as soon as CPU time is available. When CPU time is assigned to a process its state will be changed to *running*. Also, the state of the process can be *waiting*. An example of a situation where a process' state is changed to waiting state is when it makes an I/O request (e.g. read from the hard disk), its state will be *waiting* since it's waiting for the I/O device to fulfill the request. The state information about a process is stored in the process control block which is, as mentioned earlier, an entry in the processes table.

Sometimes, some processes in a system need to communicate with each other to share some data or tell each other to perform a specific operation, this leads to a broad topic known as *inter-process communication* (IPC) which provides mechanisms to make this type of communication possible. The applications of `IPC` are not restricted to operating system kernels, they are used in distributed computing for instance. One well known mechanism of `IPC` is *shared memory*, that is, a region of memory is made accessible by more than one process, each process can read and write to this region in order to share data. The ability to write to the same place by more than one process can cause a problem known as a *race condition*. Given a shared variable, the situation in which two or more processes try to change the value of this variable at the same moment is known as a race condition. There are multiple solutions for this problem and this topic is studied in a branch known *concurrency control*. Concurrency control is needed by many applications, one instance of them are database management systems (DBMS) which need these mechanisms when two users try to update the same row at the same time.

Processes are not the only entities that need to communicate, there is another unit of work which is known as a *thread* and it can be described as a lightweight process. A process can have more than one thread and when a program uses more than one thread to do its job, it is described as *multithreaded*. Threads are everywhere in our usage of computers, and a world without them is unimaginable. For example, when you use a text editor, the main thread of the program lets you write your text, but when you click on the save icon a separate thread within the text editor's process is used to perform this operation. Furthermore, another thread can be used for the spell checker while you are typing. If all their functionalities were on the same thread, you would need to wait until each one of them finishes in order to let you perform any other functionality, that is, a program without threads is going to run sequentially while threads provide us with concurrency within one process. Threads and processes have many similarities, for example, both of them are there to be executed, hence, they need to use the processor and both of them need to be scheduled to give every one of them time from the processor. In contrast to processes, threads run as a part of same process and they share the same address space which makes the communication between them much easier since they can reach the same memory by default.

## The Basics of Multitasking
When we write a kernel, many design decisions must be made [^2] and the topic of process management is not an exception. There are multiple well-known answers for some basic design questions, each one of those answers tries to solve a problem that was faced by the person who developed the solution. For example, one of the well-known features of modern operating systems is *multitasking* which is the successor of *monotasking* and both of them can be considered to be answers to a design question in operating systems. In multitasking environments, the system can run multiple processes at the same time even if there is only one processor available. In monotasking environments on the other hand, the system can run only one process at a time and the process must run until it finishes its work or the user closes it, only after that, another process can be run.

### Multiprogramming & Time-Sharing
In the days of monotasking, we were facing a serious problem that led to the birth of multitasking. It has been noticed that the processes tend to have idle time. For example, when a process is waiting for the hard disk to fetch some stored data, the process will be idle while it has the processor assigned to it exclusively, which means that the processor is under the control of a process that currently doesn't use the assigned CPU time for something useful. In this case, this means that we're wasting the valuable resource of CPU time by waiting for some non-CPU bound action to finish. Ideally, we would like to utilize the processor as much as possible without idle times, especially if there is other work to do for the CPU, and here came the solution for this problem by letting the kernel to have a list of processes that are *ready* to run.

Assuming the machine has just one processor with one core, the CPU time will be given to, say process `A`, for some time. At some point during this time the process `A` requests some data from the disk and due to that it becomes idle waiting for disk to respond. Instead of allowing process `A` to keep the control of the processor, which is doing nothing but waiting and wasting CPU cycles, the kernel suspends the process `A` and gives the CPU time to another process that has the ready state, say process `B`, This switching between two processes is known as a *context switch*. The process `B` is going to use the processor while process `A` is waiting for the disk to respond. At some point, process `B` will perform some action that makes it idle which means that the kernel can switch to another ready process and so on. This solution is known as *multiprogramming*. To sum it up, we have a list of ready processes, choose one, give it the CPU time and wait for it until it becomes idle, since it's waiting for something else to complete, we switch to another process which is ready an so on.

Better yet, multiprogramming has been extended to utilize the processor more efficiently. Instead of waiting for the currently running process to perform something which makes it idle, why don't we suspend it after some period of running time whether it is idle or not and switch to another process? This solution is known as *time sharing* which, combined with multiprogramming, represent the scheme that modern operating systems use for multitasking. In time sharing, a list of ready processes is available for the kernel to choose from, in each unit of time, say for example, every `1` second (in practice, it is shorter) the currently running process is suspended by the kernel and another process is given the CPU time and so on.

### Process Scheduling
You may recall from the previous chapter, \ref{ch-progenitor}, the system timer which emits an interrupt every unit of time, this interrupt can be used to implement time sharing in order to switch between the processes of the system. Of course, the kernel needs an algorithm to choose which process to run next, this kind of algorithms is known as *scheduling algorithms* and in general this part of the topic is known as *scheduling* in which we try to find the best way of choosing the next process to run in order to satisfy our requirements.

The *scheduler* is the part of the kernel that schedules the next process by using a scheduling algorithm, that is, it decides the next process to run based on this algorithm and performs the context switching. There are many scheduling algorithms to deal with different requirements, one of them is known as *round-robin*. With this algorithm, each process is given a fixed amount of CPU time known as *quantum*, when the running process exceeds its quantum the scheduler will be called and the CPU time will be given to the next process in the list until its quantum is used up and so on until the scheduler reaches to the end of the process list where it starts with the first process again. The value of the quantum is decided upon by the kernelist, an example value can be `50` milliseconds, which means each process will run for `50` milliseconds then be suspended, then the next one on the list will be run and so on.

### Process Context
As you know, when a process is executing, it can use the registers of the processor (e.g. `EAX`) to store its own data. Also, it may change the values of the segment registers in case it is running on a system that employs segmented memory instead of the flat memory model. Furthermore, the value of the instruction pointer `EIP` will contain an address which belongs to the process' address space. All the values that are related to a process and stored inside the registers of the processor are known as *process context*. Another term that may also be used in some places to mean the same thing is the *process state*, but don't confuse this concept with the one that we have defined with the term "state" previously, it is better to use the term process context to avoid confusion.

When a scheduler decides to change the currently running process, let's call it `A`, through a context switch, a copy of the context of the process `A` should be taken and stored somewhere, that is, a snapshot of the last context of `A` is taken before switching to another process. By taking this snapshot, it will be easy later on to resume process `A` by just loading its context to the processor's registers and jump to the value of `EIP` which has been previously stored.

### Preemptive & Cooperative Multitasking
Both multiprogramming and time-sharing solutions give us a type of multitasking known as *preemptive multitasking*, a running process is forced by the kernel to give the CPU time to another process and no process can take over the processor for the whole time. Another type of multitasking is known as *cooperative multitasking* (or *non-preemptive multitasking*), in this type the context switching is not performed forcibly, instead, the currently running process should cooperate and voluntarily tell the kernel when it should be suspended and a context switch should be performed. One of the obvious problems of this way, at least for the well-known workloads (e.g. servers or desktops), that a process, which runs code that has been written by someone we don't know, cannot be trusted. It may simply take over the CPU time and never cooperate with the kernel and never finish running due to an error in the code or even on purpose [^3].

## Multitasking in x86
With the assistance of the system timer, multitasking can be realized fully by the kernel, that is, by the kernel code. This type is known as *software multitasking*, the kernel itself is responsible for storing the list of processes and their related information, also, it's responsible for storing a snapshot of the process context before performing context switching and restoring this snapshot when the process is resumed. On the other hand, in x86 some features are provided to handle these things with the assistance of the processor itself, this type is known as *hardware multitasking*.

While hardware multitasking is available in x86, the modern operating system kernels don't use it, instead, multitasking is implemented by the kernel itself. One reason for this decision is portability. Modern kernels tend to run on more than one architecture and not only x86, by using as little of architecture's features as possible it's easier to port a kernel to other architectures.

In this section, we are going to cover the basics of hardware multitasking in x86 which are needed to initialize the environment to make it work correctly, in the same way we initialized the `GDT` for the flat memory model. Furthermore, I think knowing all available options is important, especially for kernelists. In the 539kernel we are going to implement software multitasking like in other modern kernels.

### Task State Segments
The most basic component of hardware multitasking in x86 is known as the *task state segment* (TSS) [^4] which is a segment in the memory like any other code or data segment. It has what other segments have, a base address, a limit and properties. The difference to code and data segments is that the `TSS` is a system segment [^5], this segment stores the context of a specific process.

In hardware multitasking, each process should have its own `TSS`, and each `TSS` should have an entry in the `GDT` table, that is, a *TSS descriptor*. A special register known as the *task register* contains the segment selector of the currently running process' `TSS` descriptor, the instruction `ltr` is used to store a value in this register.

![Figure 1: The Structure of the Task State Segment](Figures/process-ch/tss.png){#fig:tss width="45%"}

Figure [1](#fig:tss) shows the structure of a task state segment. As you can see, most of the fields are register values while the others are out of our topic's scope except for the previous task link which will be covered in a moment. You can see that the stack segment register and the stack pointer register have four entries instead of one, `SS`, `SS0`, `SS1` and `SS2` for the stack segment register and `ESP`, `ESP0`, `ESP1` and `ESP2` for the stack pointer register. These fields point to the stack that should be used when the process is in a specific privilege level, for example, `SS0:ESP0` will be used as the stack of the process when it switches to privilege level `0`, when it switches back to privilege level `3` the stack `SS:ESP` will be used instead, and the same is applicable to the other similar fields. If we intend to implement software multitasking, the sole reason of defining at least one `TSS` is due to these fields, when a switch between privilege levels occurs, the processor needs a `TSS` to use these fields from it in order to switch between stacks. This is needed only when the system runs user-space code, that is, privilege level `3` code.

The structure of the `TSS` descriptor in the `GDT` table is the same as the segment descriptor that we have already explained in chapter \ref{ch-x86}. The only difference is in the *type field* which has the static binary value `010B1` in the `TSS` descriptor where `B` in this value is known as the `B` flag, or *busy flag* which should be `1` when the process that this TSS descriptor represents is active and `0` when it is inactive.

### Context Switching in x86
One way of switching from a process to another [^6] in x86 hardware multitasking is to call or jump to the TSS descriptor in the `GDT`. Imagine that the system timer caused the call of the scheduler which selects process `A` as the next process to run. The scheduler can cause a context switch by using the instructions `call` or `jmp` and the operand should be the segment selector of `A`'s TSS descriptor. In this case, the processor is going to take a copy of currently running process context (call it `B`) and store it in `B`'s own `TSS`, then the values in `A`'s TSS will be loaded into the processor registers and then execution of `A` will begin.

Another way of context switching in x86 hardware multitasking is to call or jump to a task gate. In chapter \ref{ch-x86}, when we discussed the descriptors of the `IDT`, we have said that one of the descriptor types that can be defined is a task gate descriptor. This kind of descriptor is considered as a separate process by the processor, when we jump or call a task gate, the previously explained mechanism of task switching will be performed. Task gates can also be defined in the `GDT` and the `LDT`. In the `IDT` table of the 539kernel we have chosen not to define the interrupts as task gates, we don't want to perform a context switch with each interrupt.

When a process is called instead of jumped to, eventually, it should return to the caller process by using the instruction `iret`, for the processor, to be able to decide which task is the caller, the previous task link field of the callee's `TSS` will be updated to contain the segment selector of the caller process. In this way, when the `iret` instruction is executed, the processor can easily find out which process to switch back to.

## Process Management in the 539kernel
The final result of this section will be what we'll call version `T` of the 539kernel which will have basic multitasking capabilities. The multitasking style that we are going to implement is time-sharing multitasking. Also, instead of depending on x86 features to implement multitasking in the 539kernel, software multitasking will be implemented. The final `Makefile` of version `T` is provided in the last subsection, however, if you wish to build and run the kernel incrementally after each change on the progenitor you can refer to that `Makefile` and add only the needed instructions to build the intermediate increments of version `T`. For example, as you will see in a moment, the new files `screen.c` and `screen.h` will be added in version `T` as a first increment, to run the kernel after adding them you need to add the command to compile them and link them with the previous files, you can find these commands in the final version of `Makefile` as we have said before.

Our first step of this implementation is to setup a valid task state segment. While the 539kernel implements software multitasking, a valid TSS is needed. As we have said earlier, it will not be needed in our current stage but we will set it up anyway. Its need will show up when the kernel will allow user-space software to run. After that, the basic data structures for the process table and the process control block are implemented. These data structures and their usage will be as simple as possible since we don't have any means for dynamic memory allocation, yet! After that, the scheduler can be implemented and system timer's interrupts can be used to enforce preemptive multitasking by calling the scheduler every period of time. The scheduler uses the round-robin algorithm to choose the next process that will be assigned CPU time, and the context switching is performed after that. Finally, we are going to create a number of processes to make sure that everything works fine.

Before getting started with the plan that has been just described, we need to organize our code a little bit since it's going to become larger starting from this point on. Two new files should be created, `screen.c` and its header file `screen.h`. We move the printing functions that we've defined in the progenitor and their related global variables to `screen.c` and their prototypes should be in `screen.h`, so that we can `include` the latter in other C files when we need to use the printing functions. The following snippet shows the contents of `screen.h`:

``` {.c}
volatile unsigned char *video;

int nextTextPos;
int currLine;

void screen_init();
void print( char * );
void println();
void printi( int );
```

As you can see, a new function `screen_init` has been introduced while the others are same as the ones that we already wrote. The function `screen_init` will be called by the kernel once it starts running, the function initializes the values of the global variables `video`, `nextTextPos` and `currLine`. Its code is shown in the following snippet, it should be placed in `screen.c`, at the beginning of this file, `screen.h` should be included by using the line `#include "screen.h"`:

``` {.c}
void screen_init()
{
    video = 0xB8000;
    nextTextPos = 0;
    currLine = 0;
}
```

Nothing new in here, just some organizing. Now, the prototypes and implementations of the functions `print`, `println` and `printi` should be removed from `main.c`. Furthermore, the global variables `video`, `nextTextPos` and `currLine` should also be removed from `main.c`. Now, the file `screen.h` should be included in `main.c` and in the beginning of the function `kernel_main` the function `screen_init` should be called.

### Initializing the Task State Segment
Setting up the TSS is very simple. First we know that the TSS itself is a region of memory (since it is a segment), so, let's allocate it. The following should be added to the end of `starter.asm`, after the includes for the files `gdt.asm` and `idt.asm`. In the following snippet a label named `tss` is defined, and inside this region of memory, whose memory address is represented by the label `tss`, we put a doubleword with the value `0`. Recall that a word is `2` bytes while a double-word is `4` bytes. So, our `TSS` contains nothing but `4` bytes worth of zeros:

``` {.asm}
tss:
    dd 0
```

As you may recall, each `TSS` needs a descriptor entry in the `GDT` table, after defining this entry, the TSS's segment selector can be loaded into the task register. Then the processor is going to think that there is one process (one `TSS` entry in `GDT`) in the environment and that this process is the current process (the segment selector of this `TSS` is loaded into the task register). Now, let's define the TSS descriptor entry in our `GDT` table. In the file `gdt.asm` we add the following entry at the end of the label `gdt`. You shouldn't forget to modify the size of the `GDT` under the label `gdt_size_in_bytes` under `gdtr` since a sixth entry has been added to the table:

``` {.asm}
tss_descriptor: dw tss + 3, tss, 0x8900, 0x0000
```

Now, let's get back to `starter.asm` in order to load TSS' segment selector into the task register. In the `start` routine and below the line `call setup_interrupts` we add the line `call load_task_register` which calls a new routine named `load_task_register` that loads the task register with the proper value. The following snippet shows the code of this routine that can be defined before the line `bits 32` in `starter.asm`:

``` {.asm}
load_task_register:
    mov ax, 40d
    ltr ax
    
    ret
```

As you can see, it's very simple. The index of the TSS descriptor in `GDT` is `40 = (entry 6 * 8 bytes) - 8 (since indexing starts from 0)`. So, the value `40d` is moved to the register `AX` which will be used by the instruction `ltr` to load the value `40d` into the task register.

### The Data Structures of Processes
When we develop a user-space program and we don't know the size of the data that this program is going to store while it's running, we usually use dynamic memory allocations. That is, regions of memory are allocated at run-time in case we need to store more data that we didn't know that it will be needed to be stored. We have encountered the run-time stack previously, and you may recall that this region of memory is dedicated to local variables, parameters and some other information that makes function invocation possible.

The other region of a process is known as run-time heap, which is dedicated to the data that we decide to store in memory while the program is running. In C, for instance, the function `malloc` is used to allocate bytes from the run-time heap. It maintains information about free and used space of the heap so the next time this function is used the allocation algorithm can decide which region should be allocated based on the required bytes to allocate.

The part that allocates memory dynamically (inside the run-time heap) and manages the related information is known as a *memory allocator* and one of the well-known allocators is Doug Lea's memory allocator ^[https://www.cs.tufts.edu/~nr/cs257/archive/doug-lea/malloc.html]. Programming languages that use a virtual machine to execute the program code (bytecode), like Java and C\#, or by using interpreters like PHP and Python, usually provide an automatic dynamic memory allocator instead of the manual memory allocator which is used by languages such as C. That is, the programmers of these languages don't need to explicitly call a function (such as `malloc`) to allocate memory in the heap at run-time, instead, the virtual machine or the interpreter allocates dynamic memory by itself and frees the regions of the heap that are not used anymore through a mechanism known as *garbage collection*.

For those who don't know, for static memory allocation, the size of data and where it will be stored in memory is known during compile-time. Global variables and local variables are examples of objects that use static memory allocation. For dynamic memory allocation, we cannot know the size of data during compile-time or whether it will be stored in the first place. This important information can only be known while the program is running, that is, during run-time. Due to that, we need to use dynamic memory allocation for this data since this type of allocation doesn't require us to know the size of data during compile-time.

The process table is an example of a data structure (object) that we can't know the size of during compile-time and this information can only be known while the kernel is running. Take your current operating system as an example, you can run any number of processes (to some limit of course) and each one of them will have an entry in the process table ^[We already know that keeping an entry of a process in the process table is important for the scheduling process and other related functionality.]. Maybe your system is running just two processes right now but you can run more and more without the need of recompiling the kernel in order to increase the size of the process table.

That's possible due to usage of dynamic memory allocation when a new process is created during run-time. It works by dynamically allocating a chunk of space in the run-time heap through the memory allocator for the entry of the new process. When this process finishes its job (e.g. the user closes the application), the memory region that was used to store its entry in the process table is marked as free space so it can be used to store something else in the future, for example, the entry of another process.

In our current situation, we don't have any means of dynamic memory allocation in the 539kernel, this topic will be covered when we start discussing memory management. Due to that, our current implementation of the process table and process control block are going to use static memory allocation through global variables. That of course, restricts us from creating a new process on-the-fly, that is, at run-time. But our current goal is to implement basic multitasking that will be extended later. To start our implementation, we need to create new two files, `process.c` and its header file `process.h`. Any function or data structure that is related to processes should belong into these files.

#### Process Control Block
A process control block (PCB) is an entry in the process table, it stores the information that is related to a specific process, the state and context of the process are examples of such information. In the 539kernel, there are two possible states for a process, either a process is *running* or *ready*. When a context switch is needed to be performed, the context of the currently running process, which will be suspended, should be stored in its own PCB. As discussed earlier, the context of a process in the 539kernel consists of the values that were stored in the processor's registers before suspending a process.

Each process in the 539kernel, as in most modern kernels, has a unique identifier known as *process id* or PID for short. This identifier is also stored in the PCB of the process. Now, let's define the general structure of the PCB and its components in the 539kernel. These definitions should reside in `process.h`:

``` {.c}
typedef enum process_state { READY, RUNNING } process_state_t;

typedef struct process_context
{
    int eax, ecx, edx, ebx, esp, ebp, esi, edi, eip;
} process_context_t;

typedef struct process
{
    int pid;
    process_context_t context;
    process_state_t state;
    int *base_address;
} process_t;
```

As you can see, we start with the type `process_state_t`, any variable that has this type may have two possible values, `READY` or `RUNNING`, they correspond the two possible states of a process and this type will be used for the state field in the PCB definition.

Next, the type `process_context_t` is defined. It represents the context of a process in the 539kernel and you can see it is a C structure that is intended to store a snapshot of x86 registers that can be used by a process.

Finally, the type `process_t` is defined which represents a process control block, that is, an entry in the process table. A variable of type `process_t` represents one process in the 539kernel environment. Each process has following fields:
- a `pid` field which is its unique identifier
- a `context` field which is the snapshot of the environment before suspending the process
- a `state` field which indicates whether a process is `READY` to run or currently `RUNNING`
- a `base_address` field which is the memory address of the starting point of the process' code (think of `main()` in C), that is, when the kernel intends to run a process for the first time, it should jump to the `base_address`, in other words, set `EIP` register to `base_address`.

#### Process Table
As we mentioned earlier, currently we're going to depend on static memory allocation since we don't have any way to do dynamic memory allocation. Due to that, our process table must be very simple, it's an array of type `process_t`. Usually, a more advanced data structure is used for the processes list based on the requirements which are decided by the kernelist, the *linked list data structure* is a well-known choice. The following definition should reside in `process.h`. Currently, the maximum size of the 539kernel process table allows for `15` processes, feel free to increase it but don't forget, it will, still, be a static size:

``` {.c}
process_t *processes[ 15 ];
```

### Process Creation
Now, we are ready to write the function that creates a new process in the 539kernel. Before getting started with the implementation of the required functions, we need to define their prototypes and some auxiliary global variables in `process.h`:

``` {.c}
int processes_count, curr_pid;

void process_init();
void process_create( int *, process_t * );
```

The first global variable `processes_count` represents the current number of processes in the environment, this value will become handy when we write the code of the scheduler which uses the round-robin algorithm. Simply said, whenever a process is created in the 539kernel, the value of this variable is increased and since deleting a process won't be implemented for the sake of simplicity, the value of this variable won't be decreased anywhere in the current code of the 539kernel.

The global variable `curr_pid` contains the next available process identifier that can be used for the next process that will be created. The value of this variable is used when creating a new process and its value is increased by one after completing the creation.

The function `process_init` is called when the kernel starts, and it initializes the process management subsystem by just initializing the two global variables that we've mentioned.

The function `process_create` is the one that creates a new process in the 539kernel, that is, it is equivalent to `fork` in Unix systems. As you can see, it takes two parameters, the first one is a pointer to the base address of the process, that is, the starting point of the process' code. The second parameter is a pointer to the process control block. As we have said, currently, we use static memory allocation, therefore, each new PCB will be either stored in memory as a local or global variable, so, for now, the caller is responsible for statically allocating memory for the PCB and passing its memory address in the second parameter. In normal circumstances, when dynamic memory allocation is available, the memory of a PCB is allocated dynamically by the creation function itself, but that's a story for another chapter. The following snippet shows the contents of `process.c` we've just described:

``` {.c}
#include "process.h"

void process_init()
{
    processes_count = 0;
    curr_pid = 0;
}

void process_create( int *base_address, process_t *process )
{   
    process->pid = curr_pid++;
    
    process->context.eax = 0;
    process->context.ecx = 0;
    process->context.edx = 0;
    process->context.ebx = 0;
    process->context.esp = 0;
    process->context.ebp = 0;
    process->context.esi = 0;
    process->context.edi = 0;
    process->context.eip = base_address;
    
    process->state = READY;
    process->base_address = base_address;
    
    processes[ process->pid ] = process;
    
    processes_count++;
}
```

In `process_create`, a new process identifier is assigned to the new process, then the context is initialized. This structure will be used later in context switching, either by copying the values from the processor to the structure or vice versa. Since the new process has not been run yet, hence, it didn't set any values to the registers, we initialize all the general purpose registers with `0`. Later on, when this process runs and the scheduler decides to suspend it, the values that this process wrote into the real registers will be copied in here. The program counter `EIP` structure field is initialized with the starting point of the process' code, in this way we can make sure that when the scheduler decides to run this process, it loads the correct value into the register `EIP`.

After initializing the context, the state of the process is set to `READY` to run and the base address of the process is stored in a separate field. Then, the newly-created PCB is added to the process list and finally the number of processes in the system is increased by one.

That's all we need for now to implement multitasking. In the real world, there will be usually more process states such as *waiting*, the data structures will be allocated dynamically to make it possible to create virtually any number of processes, the PCB will usually contain more fields and more functions to manipulate the process table (e.g. delete process) will be implemented. However, our current implementation, though very simple, is enough to serve as a working foundation. Now, in `main.c`, the header file `process.h` needs to be included, and the function `process_init` should be called at the beginning of the kernel, after the line `screen_init();`.

### The Scheduler
Right now, we have all the needed components to implement the core of the multitasking functionality, that is, the scheduler. As mentioned multiple times before, the round-robin algorithm is used for the 539kernel's scheduler.

Let's present two definitions to make our next discussion clearer. The term *current process* means the process that is using the processor right now. At some point in time, the system timer emits an interrupt which suspends the current process and calls the kernel to handle the interrupt. In the according interrupt handler, the kernel is going to call the scheduler. At this point in time, while the interrupt handler is running, we will still keep calling the process which was running right before calling the kernel the current process. By using some algorithm, the scheduler chooses the *next process*, that is, the process that will run after the scheduler finishes its work and the kernel returns the processor to the processes. After choosing the next process, performing the context switching and jumping to the process code, this chosen process will be the current process instead of the previous one. The previously running process will now be in a suspended state. The newly chosen process will be the current process until the next run of the scheduler and so on.

Now, we are ready to implement the scheduler. Let's create a new file `scheduler.c` and its header file `scheduler.h` for the new code. The following snippet shows the contents of the header file:

``` {.c}
#include "process.h"

int next_sch_pid, curr_sch_pid;

process_t *next_process;

void scheduler_init();
process_t *get_next_process();
void scheduler( int, int, int, int, int, int, int, int, int );
void run_next_process();
```

First, `process.h` is included since we need to use the structure `process_t` in the code of the scheduler. Then three global variables are defined. The global variable `next_sch_pid` stores the PID of the next process that will run after the next system timer interrupt, while `curr_sch_pid` stores the PID of the currently running process. The global variable `next_process` stores a reference to the PCB of the next process, this variable will be useful when we want to pass the control of the processor from the kernel to the next process which is the job of the function `run_next_process`.

The function `scheduler_init` sets the initial values of the global variables, in the same way as `process_init`, it will be called when the kernel starts.

The core function is `scheduler` which represents the 539kernel's scheduler, this function will be called when the system timer emits its interrupt. It chooses the next process to run with the help of the function `get_next_process`, performs context switching by copying the context of the current process from the registers to the memory and copying the context of the next process from the memory to the registers. Finally, it returns and `run_next_process` is called in order to jump to the next process' code. In `scheduler.c`, the file `scheduler.h` should be included to make sure that everything is in place. The following snippet shows the implementation of `scheduler_init`:

``` {.c}
void scheduler_init()
{
    next_sch_pid = 0;
    curr_sch_pid = 0;
}
```

It's a very simple function that initializes the values of the global variables by setting the PID `0` to both of them, so the first process that will be scheduled by the 539kernel is the process with the PID `0`.

Next, let's look at the definition of `get_next_process` which implements the round-robin algorithm. It returns the PCB of the process that should run next and prepare the value of `next_sch_pid` for the next context switching cycle by using the round-robin policy:

``` {.c}
process_t *get_next_process()
{
    process_t *next_process = processes[ next_sch_pid ];
    
    curr_sch_pid = next_sch_pid;
    next_sch_pid++;
    next_sch_pid = next_sch_pid % processes_count;
    
    return next_process;
}
```

Very simple, right? [^10] If you haven't encountered the symbol `%` previously, it represents an operation called *modulo* which gives the remainder of the division operation, for example, `4 % 2 = 0` because the remainder of dividing `4` by `2` is `0`, but `5 % 2 = 1` because `5 / 2 = 2` and the remainder is `1`, so, `5 = ( 2 * 2 ) + 1` (`1` being the remainder).

In the modulo operation, any value `n` that is in the same position as `2` in the previous two examples is known as *modulus*. For instance, the modulus in `5 % 3` is `3` and the modulus in `9 % 10` is `10` and so on. Sometimes, the operator `mod` is used to represent the modulo operation instead of `%`.

The interesting thing about modulo is that its result is always in the range of `0` and `n - 1` given that `n` is the modulus. For example, let the modulus be `2`, and we perform the modulo operation `x % 2` where `x` can be any number, the possible results of this operation can be only `0` or `1`. Using this example with different values of `x` gives us the following results: `0 % 2 = 0`, `1 % 2 = 1`, `2 % 2 = 0`, `3 % 2 = 1`, `4 % 2 = 0`, `5 % 2 = 1`, `6 % 2 = 0`, and so on to infinity!

As you can see, the modulo operation gives us a cyclic sequence that starts at `0` and ends at some value that is related to the modulus `n` and starts all over again with the same cycle if the input an ordered sequence of values. Sometimes the analog clock is used as a metaphor to describe the modulo operation. In mathematics the topic known as *modular arithmetic* is dedicated to the modulo operation. You may have noticed that the modulo operation can be handy to implement the round-robin algorithm.

Let's get back to the function `get_next_process` which chooses the next process to run in a round-robin fashion. As you can see, it assumes that the PID of the next process is stored in `next_sch_pid`. By using this assumption it fetches the PCB of this process to return it later to the caller. After that, the value of `curr_sch_pid` is updated to indicate that, from now on, the current process is the one that we just selected to run next. The next two lines are the core of the operation of choosing the next process to run, it changes the `next_sch_pid` and thus decides which process will run when the next system timer interrupt occurs.

Assume that the total number of processes in the system is `4`, that is, the value of `processes_count` is `4`, and assume that the next process to run after the system timer interrupt occurs has the PID `3`, that is `next_sch_pid = 3`. PIDs in the 539kernel start from `0`, that means there is no process with PID `4` in our example and process `3` is the last one.

In line `next_sch_pid++` the value of the variable will be incremented to `4`, and as we mentioned, the last process is PID `3` and there is no process which has the PID `4`. That means we should jump back to the start of the list of processes and run process `0` in the next cycle. We can do that simply by using modulo on the new value of `next_sch_pid` with the modulus `4` which is the number of processes in the system and the current value of `process_count`, so, `next_sch_pid = 4 % 4 = 0`. In the next cycle, the process with the PID `0` will be chosen to run, the value of `next_sch_pid` will be updated to `1` and since it is smaller than `process_count` it will be kept for the next cycle. After that, process `1` will run and the next process to run will be PID `2`. Then process with the PID `2` will run and next process to run will be PID `3`. Finally, the same situation that we started our explanation with will occur again and the process with the PID `0` will again be chosen to run next. The following snippet shows the code of the function `scheduler`:

``` {.c}
void scheduler( int eip, int edi, int esi, int ebp, int esp, int ebx, int edx, int ecx, int eax )
{
    process_t *curr_process;
    
    // ... //
    
    // PART 1
    
    curr_process = processes[ curr_sch_pid ];
    next_process = get_next_process();
    
    // ... //
    
    // PART 2

    if ( curr_process->state == RUNNING )
    {
        curr_process->context.eax = eax;
        curr_process->context.ecx = ecx;
        curr_process->context.edx = edx;
        curr_process->context.ebx = ebx;
        curr_process->context.esp = esp;
        curr_process->context.ebp = ebp;
        curr_process->context.esi = esi;
        curr_process->context.edi = edi;
        curr_process->context.eip = eip;
    }
    
    curr_process->state = READY;
    
    // ... //
    
    // PART 3
    
    asm( "  mov %0, %%eax;  \
            mov %0, %%ecx;  \
            mov %0, %%edx;  \
            mov %0, %%ebx;  \
            mov %0, %%esi;  \
            mov %0, %%edi;" 
            : : "r" ( next_process->context.eax ), "r" ( next_process->context.ecx ), "r" ( next_process->context.edx ), "r" ( next_process->context.ebx ),
                "r" ( next_process->context.esi ), "r" ( next_process->context.edi ) );
    
    next_process->state = RUNNING;
}
```

The code is commented to divide it into three parts for the sake of simplicity in our discussion. The first part is simple, the reference to the PCB of the current process which has been suspended due to the system timer interrupt is assigned to the variable `curr_process`, this will become handy in part `2` of scheduler's code. We get the reference to the current process before calling the function `get_next_process` because, as you know, this function changes the global variable that holds the current process' PID (`curr_sch_pid`) from the suspended one to the next one [^11]. After that, the function `get_next_process` is called to obtain the PCB of the process that will run next.

As you can see, `scheduler` receives nine parameters, each one of them has a name that corresponds to one of the processor's registers. We can tell from these parameters that the function `scheduler` receives the context of the current process that should be suspended due to system timer's interrupt. For example, assume that process `0` was running, after the quantum is finished the scheduler is called, which decides that process `1` should run next. In this case, the parameters that have been passed to the scheduler represent the context of process `0`, that is, the value of the parameter `EAX` will be same as the value of the register `EAX` that process `0` has set before being suspended. How do we get these values and from where do we pass them as parameters to `scheduler`? This will be discussed later.

In part `2` of the scheduler's code, the context of the suspended process, which is currently represented by `curr_process`, is stored into its PCB by using the passed parameters. Storing the current process' context into its PCB is simple as you can see, we just store the passed values in the fields of the current process' structure. These values will be used later when we decide to run the same process again. Also, we need to make sure that the current process is really running by checking its `state` before copying the context from the processor to the PCB. In the end, the `state` of the current process is switched from `RUNNING` to `READY`.

Part `3` performs the opposite of part `2`, it uses the PCB of the next process to retrieve its context that was stored before it was suspended the last time, then this context is copied to the registers of the processor. Of course, not all of them are being copied to the processor, for example, the program counter `EIP` cannot be written to directly, we will see later how to deal with it. Also, the registers that are related to the stack, `ESP` and `EBP` were skipped on purpose. As a last step, the `state` of the next process is changed from `READY` to `RUNNING`. The following snippet shows the code of `run_next_process` which is the last function in `scheduler.c`:

``` {.c}
void run_next_process()
{
    asm( "  sti;            \
            jmp *%0" : : "r" ( next_process->context.eip ) );
}
```

It's a simple function that executes two assembly instructions. First it enables the interrupts via the instruction `sti`, then it jumps to the memory address which is stored in the `EIP` of the next process' PCB. The purpose of this function will be discussed shortly.

To make everything run properly, `scheduler.h` need to be included in `main.c`, note that, when we include `scheduler.h`, the line which includes `process.h` should be removed since `scheduler.h` already includes it. After that, the function `scheduler_init` should be called when initializing the kernel, say after the line which calls `process_init`.

#### Calling the Scheduler
"So, how is the scheduler being called?", you may ask. The answer to this question has been mentioned multiple times before. When the system timer decides that it is the time to interrupt the processor, the interrupt `32` is being fired, this is exactly the moment when the scheduler is being called. In each period of time the scheduler will be called to schedule another process and give it CPU time.

In this part, we are going to write a special interrupt handler for interrupt `32` that calls the 539kernel's scheduler. First we need to add the following lines in the beginning of `starter.asm` [^12] after `extern interrupt_handler`:

``` {.asm}
extern scheduler
extern run_next_process
```

As you may have guessed, the purpose of these two lines is to make the functions `scheduler` and `run_next_process` of `scheduler.c` usable by the assembly code of `starter.asm`. Now, we can get started with the implementation of interrupt `32`'s handler which calls the scheduler with the needed parameters. In the file `idt.asm` the old code of the routine `isr_32` should be changed to the following:

``` {.asm}
isr_32:
    ; Part 1
    
    cli ; Step 1
    
    pusha ; Step 2
    
    ; Step 3
    mov eax, [esp + 32]
    push eax
    
    call scheduler ; Step 4
    
    ; ... ;
    
    ; Part 2
    
    ; Step 5
    mov al, 0x20
    out 0x20, al
    
    ; Step 6
    add esp, 40d
    push run_next_process
    
    iret ; Step 7
```

There are two major parts in this code. The first part is the code which will be executed before calling the scheduler, that is, the one before the line `call scheduler`. The second part is the code which will be executed after the scheduler returns.

The first step of part one disables the interrupts via the instruction `cli`. When we are handling an interrupt, it is better to not receive any other interrupt, if we don't disable interrupts here, while handling a system timer interrupt, another system timer interrupt can occur even before calling the scheduler for the first time, you can imagine what mess that can cause.

Before explaining the steps two and three of this routine, we need to answer a vital question: When this interrupt handler is called, what will be the context of the processor? The answer is, the context of the suspended process, that is, the process that was running before the system timer emitted the interrupt. That means all values that were stored by the suspended process on the general purpose registers will be there when `isr_32` starts executing and we can be sure that the processor did not change any of these values while suspending the process and calling the handler of the interrupt. What gives us this assurance is the fact that we have defined all `ISR` gate descriptors as interrupt gates in the `IDT` table, if we would have defined them as task gates, the context of the suspended process wouldn't be available directly in processor's registers. Defining an `ISR` descriptor as an interrupt gate makes the processor call this `ISR` like a normal routine by following the calling convention. It's important to remember this when we discuss how to obtain the value of `EIP` of the suspended process later on in this section.

We know that the context of the suspended process is reachable via the registers (e.g `EAX`), so we can store a copy of them on the stack, this snapshot will be useful when the scheduler needs to copy the context of the suspended process to memory as we have seen. Also, pushing them onto the stack gives us two more benefits. First we can begin to use the registers in the current code as we see fit without the fear of losing the suspended process' context because it's already stored on the stack and we can refer to it anytime we need it. Second, according to the calling convention that we have discussed in chapter \ref{ch-x86} these pushed values can be viewed as parameters for a function that will be called from our code. That's exactly how we pass the context of the suspended process to the function `scheduler` as parameters, simply by pushing the values of the general purpose registers onto the stack.

Now, instead of writing `8` push instructions to push these values onto the stack, for example `push eax` and so on, there is an x86 instruction named `pusha` which pushes the current values of all general purpose registers onto the stack. That's exactly what happens in the second step of `isr_32` in order to send them as parameters to the function `scheduler`. The reverse operation of `pusha` can be performed by the instruction `popa`, that is, the values on the stack will be loaded into the registers.

The instruction `pusha` pushes the values of the registers in the following order: `EAX`, `ECX`, `EDX`, `EBX`, `ESP`, `EBP`, `ESI` and `EDI`. Based on the calling convention they will be received as parameters in the reversed order, that is, the first pushed value will be the last parameter for the callee, so, the parameter that contains the value of `EDI` comes before `ESI` in the parameters list and so on. You can see that in an obvious way in the parameters list of the function `scheduler`.

The only missing piece now is the value of the instruction pointer `EIP`. The third step of `isr_32` obtains this value. As you know, it is very important to store the last value of `EIP` of the suspended process. We need to know where the execution of the suspended process code did stop so we can resume its work later from the same point, and this information is stored in `EIP`.

Unlike the general purpose registers, the value of `EIP` will not be pushed onto the stack by the instruction `pusha`. Furthermore, the current value of `EIP` is by no means a pointer to where the suspended process stopped. As you know, the current value of `EIP` is a pointer to the current instruction which is being executed right now, that is, one of the `isr_32` instructions. So, the question is, where can we find the value of `EIP` which was there just before the suspended process has been suspended? The answer can be found again in the calling convention.

![Figure 2: The Stack After Executing the Instruction `pusha`](Figures/process-ch/Fig21092021_1.png){#fig:21092021_1 width="35%"}

Let's assume that a process named `A` was running and a system timer interrupt occurred which caused process `A` to suspend and `isr_32` to start. As we have mentioned earlier, `isr_32` will be called like a normal routine and the calling convention will be followed by the processor. Figure [2](#fig:21092021_1) shows the stack after executing the instruction `pusha` in `isr_32`. As you can see, the context of process `A` is on the stack. For example, to reach the value of `ESI` which was stored right before the process `A` has been suspended, we can refer to the memory address `ESP + 4` ^[If a new stack frame is created once `isr_32` starts then `EBP` can also be used as a base address but with a different offset than `4` of course as we have explained earlier in chapter \ref{ch-x86}. We didn't initialize a new stack frame here and in all other places mainly to get shorter code.], since the current `ESP` stores the memory address of the top of the stack, the size of the value of `EDI` (and all other registers) is `4` bytes and the value of `ESI` is next to the top of the stack.

The same technique can be used with any other value on stack. As you may have noticed in figure [2](#fig:21092021_1), the return address to the location where process `A` was suspended is stored on the stack, and that's due to the calling convention which requires the return address of the caller to be stored on the stack so we can return to it. As you can see, here, the process `A` was viewed as the caller and `isr_32` as the callee. So, to obtain the value of process `A`'s return address (and thus the value of its `EIP` register at the moment it was suspended), we can simply read the value in `esp + 32`. The value is calculated as follows: `32 = 4 * 8`, `8` being the count of variables pushed onto the stack since the start of `isr_32` via the instruction `pusha` and `4` being the size of each of these variables in bytes. And that is exactly what we've done in the third step of the `isr_32` code, we first read this value and then pushed it onto the stack so the function `scheduler` can receive it as the first parameter.

The fourth and fifth steps are simple: in the fourth step we call the function `scheduler` which we have already discussed. After the function `scheduler` returns, we need to tell the PIC that we've finished the handling of an `IRQ` by sending the end of interrupt command to the `PIC` and that's what is performed in the fifth step. We have already discussed sending the end of interrupt command to the PIC in chapter \ref{ch-progenitor}.

The final thing to do after choosing the next process and performing the context switch is to transfer control to the next process, let's call it process `B`, thus giving its code CPU time until the next timer interrupt fires again. This is usually performed by jumping to the memory address at which the selected process was suspended. There are multiple ways to do that, the way which we have used in the 539kernel is to exploit the calling convention, again.

As we've mentioned before, the return address to the caller is stored on the stack, in our previous example, the return address to process `A` was stored on the stack right before the process `A`'s context values which have been pushed by the instruction `pusha`. When a routine returns by using the instruction `ret` or `iret`, this address will be jumped to. We exploit this fact to make the next process `B` run after the routine `isr_32` finishes instead of the previous process `A`. This is quite simple to achieve, the return address of process `A` must be removed from the stack and in its position on the stack the resume point of process `B` must be pushed. That's exactly what we do in the sixth step of `isr_32`.

First we remove all values that we've pushed to the stack while running `isr_32`. This is done just by adding `40d` to the current value of `ESP`. We've already discussed this method of removing values from the stack, but why adding `40d`, you may ask? The number of values that have been pushed by the instruction `pusha` is `8` values, each one of them of size `4` bytes (`32-bit`), that means the total size of them is `4 * 8 = 32`. Also, we have pushed the value of `EIP` which also has the size of `4` bytes, so the total size of the pushed items in `isr_32` is `32 + 4 = 36` and these are all values that were pushed to the stack by our code. We also need to remove the return address which has been pushed onto the stack before calling `isr_32`, the size of memory addresses in the `32-bit` architecture is `4` bytes (`32-bit`), that means `36 + 4 = 40` bytes should be removed from the stack to ensure that we remove all pushed values and the return address of process `A`.

After that, we simply push the memory address of the function `run_next_process`. In the seventh step, the routine `isr_32` returns indicating that handling an interrupt has been completed, but instead of returning to the suspended code before calling the interrupt handler, the code of the function `run_next_process` will be called, which, as we've seen, enables the interrupts again and jumps to the resume point of the next process. In this way, we've implemented basic multitasking!

### Running Processes
In our current environment, we won't be able to test our process management by using the normal way of doing so, meaning, we can't run a user-space program to check if its process has been created and whether it's being scheduled or not. Instead, we are going to create a number of processes by creating their `PCB`s via the `process_create` function. The code of each process will be defined as a function in our kernel and the memory address of each function will be considered as the starting point of the according process. Our goal of doing that is just to test that our process management code works correctly. All code of this section will be in `main.c` unless mentioned otherwise. First, we define the prototypes for four functions, each one of them represents a separate process, we will pretend that they represent normal use-space programs. These prototypes should be defined before `kernel_main`:

``` {.c}
void processA();
void processB();
void processC();
void processD();
```

Inside `kernel_main`, we define four local variables, each one of them represents the PCB of one process:

``` {.c}
    process_t p1, p2, p3, p4;
```

Before the infinite loop of `kernel_main` we create the four processes in the system by using the function `process_create` like in the following snippet:

``` {.c}
    process_create( &processA, &p1 );
    process_create( &processB, &p2 );
    process_create( &processC, &p3 );
    process_create( &processD, &p4 );
```

The code of the processes is shown the following snippet:

``` {.c}
void processA()
{
    print( "Process A," );

    while ( 1 )
        asm( "mov $5390, %eax" );
}

void processB()
{
    print( "Process B," );

    while ( 1 )
        asm( "mov $5391, %eax" );
}

void processC()
{
    print( "Process C," );

    while ( 1 )
        asm( "mov $5392, %eax" );
}

void processD()
{
    print( "Process D," );

    while ( 1 )
        asm( "mov $5393, %eax" );
}
```

Each process starts by printing its name, then, an infinite loop starts which keeps setting a specific value in the register `EAX`. To check whether multitasking works fine, we can add the following lines the beginning of the function `scheduler` in `scheduler.c`:

``` {.c}
    print( " EAX = " );
    printi( eax );
```

Each time the scheduler starts, it prints the value of `EAX` of the suspended process. When we run the kernel, each process is going to start by printing its name and before it starts executing the value of `EAX` of the previous process will be shown. Therefore, you will see that the following texts `EAX = 5390`, `EAX = 5391`, `EAX = 5392`, and `EAX = 5393` will keep showing up on the screen which indicates that the process, for example process `A` in case `EAX = 5390` is shown, was running and it has been suspended now to run the next one and so on.

### Finishing up Version `T`
And now we've got the complete version `T` of the 539kernel which provides us with a basic process management subsystem. The last piece to be presented is the `Makefile` to compile the all of the source files:

``` {.makefile}
ASM = nasm
CC = gcc
BOOTSTRAP_FILE = bootstrap.asm 
INIT_KERNEL_FILES = starter.asm
KERNEL_FILES = main.c
KERNEL_FLAGS = -Wall -m32 -c -ffreestanding -fcommon -fno-asynchronous-unwind-tables -fno-pie -fno-stack-protector
KERNEL_OBJECT = -o kernel.elf

build: $(BOOTSTRAP_FILE) $(INIT_KERNEL_FILES) $(KERNEL_FILES) screen.c process.c scheduler.c
	$(ASM) -f bin $(BOOTSTRAP_FILE) -o bootstrap.o
	$(ASM) -f elf32 $(INIT_KERNEL_FILES) -o starter.o
	$(CC) $(KERNEL_FLAGS) $(KERNEL_FILES) $(KERNEL_OBJECT)
	$(CC) $(KERNEL_FLAGS) screen.c -o screen.elf
	$(CC) $(KERNEL_FLAGS) process.c -o process.elf
	$(CC) $(KERNEL_FLAGS) scheduler.c -o scheduler.elf
	ld -melf_i386 -Tlinker.ld starter.o kernel.elf screen.elf process.elf scheduler.elf -o 539kernel.elf
	objcopy -O binary 539kernel.elf 539kernel.bin
	dd if=bootstrap.o of=kernel.img
	dd seek=1 conv=sync if=539kernel.bin of=kernel.img bs=512 count=8
	dd seek=9 conv=sync if=/dev/zero of=kernel.img bs=512 count=2046
	qemu-system-x86_64 -s kernel.img
```

The only new part here whose purpose isn't immediately obvious is the compiler flag `-fcommon`. Currently, we compile the kernel piece by piece by creating object files from source files and then combining the pieces with the linker (`ld`) into a single binary. This will still work, even if we have multiple source files as long as we don't define global variables or define them only in `main.c` because that's the file that includes all other source files, directly or indirectly, but is never included by other source files. As soon as we start including sources that contain global variable declarations in multiple places, as is the case at least for `screen.h` which is included by `scheduler.c` and `main.c` to print some debug outputs, the linker will complain that we've defined the same global variable in multiple places, which is apparently forbidden by default.

The problem here is that each time we include a header file (via `#include "screen.h"`, for example) the compiler evaluates this header file for the current compilation unit to resolve all symbols and includes all the resolved symbols, including the global variables, into the resulting object file. When the linker then assembles the ELF executable from the object files, it finds multiple declarations of the same global variable that were created each time we included a header file that defined a global variable.

Usually, this problem is mitigated by adding preprocessor directives in each header file that effectively allow the inclusion of a header file only once. These directives look like the following picking `header.h` as an example:

``` {.c}
#ifndef SCREEN_H
#define SCREEN_H

// some declarations

#endif
```

We can't prevent the compiler to evaluate the header files only once here because we're compiling the object files one by one. It simply doesn't know that a specific header was already included in a different compilation unit because they're all created separately. The flag `-fcommon` changes the way the compiler handles the placement of uninitialized global variables in object files, it basically allows the merging of the global definitions by the linker which resolves the initial problem.

Apart of the aforementioned change, there's nothing surprising in here, only additional instructions to compile the new C files that we've added to the 539kernel.

[^1]: We mean static data here, which is part of the binary file
    of the program. Data that is generated by the running
    process is not loaded from the binary file, instead it's
    created while the code is running (e.g. local variables on the
    stack).

[^2]: Remember, it's the job of a kernelist!

[^3]: You may ask who would use cooperative multitasking and give this
    amount of trust to the program code! In fact, the versions of
    Windows before 95 used this style of multitasking, also, Classic Mac
    OS used it. Why, you may ask? I don't know exactly, but what I know
    for sure is that humanity is in a learning process!

[^4]: In x86, the term task is used instead of process.

[^5]: In chapter \ref{ch-x86} we have seen that there are two types of segments in x86: application segments such as code, data and stack segment, and system segments such as `LDT` and `TSS`.

[^6]: In x86, a context switch is known as task switch.

[^10]: Could be simpler, but the readability is more important here.

[^11]: And that's why global variables are considered evil.

[^12]: I'm about to regret that I called this part of the kernel the starter! Obviously, it's more than that!
