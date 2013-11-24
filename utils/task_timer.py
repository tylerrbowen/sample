import threading
from threading import Thread, Event
import Queue
import time
import calendar


class NewTimer(object):

    def __init__(self, name):
        self.name = name
        self.queue = TaskQueue()
        self.thread = TimerThread(self.queue)
        self.thread.setName(name)
        self.thread.start()

    def schedule(self, task, delay):
        if delay < 0:
            raise TypeError('Negative Delay')
        self.sched(task, calendar.timegm(time.gmtime())+delay, 0)

    def sched(self, task, time, period):
        if time < 0:
            raise TypeError('Illegal Execution Time')

        # Constrain value of period sufficiently to prevent numeric
        #// overflow while still being effectively infinitely large.
        if abs(period) > 0x7fffffffffffffffL >> 1:
            period >>= 1

        self.queue.mutex.acquire()
        if not self.thread.newTasksMayBeScheduled:
            raise TypeError("Timer already cancelled.")

        task.__block.acquire()
        if task.state != TimerTask.VIRGIN:
            raise TypeError(
                "Task already scheduled or cancelled")
        task.nextExecutionTime = time
        task.period = period
        task.state = TimerTask.SCHEDULED
        task.__block.release()

        self.queue.add(task)
        if self.queue.get_min() == task:
            self.queue.task_done()
        self.queue.mutex.release()

    def cancel(self):
        self.queue.mutex.acquire()
        self.thread.newTasksMayBeScheduled = False
        self.queue.clear()
        self.queue.task_done()
        self.queue.mutex.release()

    def scheduleAtFixedRate(self, task, firstTime, period):
        if (period <= 0):
            raise TypeError("Non-positive period.")
        self.sched(task, firstTime.getTime(), period)


class TaskThread(threading.Thread):
    """Thread that executes a task every N seconds"""

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self._finished = threading.Event()
        self._interval = 15.

    def setInterval(self, interval):
        """Set the number of seconds we sleep between executing our task"""
        self._interval = interval

    def cancel(self):
        """Stop this thread"""
        self._finished.set()

    def run(self):
        while 1:
            if self._finished.isSet(): return
            self.task()

            # sleep for interval or until shutdown
            self._finished.wait(self._interval)

    def task(self):
        """The task done by this thread - override in subclasses"""
        pass


class TimerTask(Thread):
    VIRGIN = 0
    SCHEDULED   = 1
    EXECUTED    = 2
    CANCELLED   = 3
    lock = object()

    def __init__(self):
        super(TimerTask, self).__init__()
        self.period = 0
        self.state = self.VIRGIN
        self.next_execution_time = 0
        self.period = None
        self.finished = Event()

    def run(self):
        pass

    def cancel(self):
        self.__block.acquire()
        result = self.state == self.SCHEDULED
        self.state = self.CANCELLED
        self.__block.release()
        return result

    def scheduled_execution_time(self):
        if self.period < 0:
            return self.next_execution_time + self.period
        else:
            return self.next_execution_time - self.period


class TaskQueue(Queue.Queue):
    """
     * Priority queue represented as a balanced binary heap: the two children
     * of queue[n] are queue[2*n] and queue[2*n+1].  The priority queue is
     * ordered on the nextExecutionTime field: The TimerTask with the lowest
     * nextExecutionTime is in queue[1] (assuming the queue is nonempty).  For
     * each node n in the heap, and each descendant of n, d,
     * n.nextExecutionTime <= d.nextExecutionTime.
    """

    def add(self, task):
        """
         * Adds a new task to the priority queue.
        """
        Queue.Queue.put(self, task)


    def get_min(self):
        """
         * Return the "head task" of the priority queue.  (The head task is an
         * task with the lowest nextExecutionTime.)
        """
        return self.queue[1]


    def get_index(self, i):
        """
         * Return the ith task in the priority queue, where i ranges from 1 (the
         * head task, which is returned by getMin) to the number of tasks on the
         * queue, inclusive.
        """
        return self.queue[i]

    def remove_min(self):
        """
         * Remove the head task from the priority queue.
        """
        Queue.Queue._get(self)


    def reschedule_min(self, new_time):
        """
         * Sets the nextExecutionTime associated with the head task to the
         * specified value, and adjusts priority queue accordingly.
        """
        self.queue[1].next_execution_time = new_time
        self.fix_down(1)


    def isEmpty(self):
        """
         * Returns true if the priority queue contains no elements.
        """
        return Queue.Queue.empty(self)


    def clear(self):
        """
         * Removes all elements from the priority queue.
        """
        self.mutex.acquire()
        for i in range(self.qsize()):
            self.queue[i] = None
        self.mutex.release()


    def fix_up(self, k):
        """
         * Establishes the heap invariant (described above) assuming the heap
         * satisfies the invariant except possibly for the leaf-node indexed by k
         * (which may have a nextExecutionTime less than its parent's).
         *
         * This method functions by "promoting" queue[k] up the hierarchy
         * (by swapping it with its parent) repeatedly until queue[k]'s
         * nextExecutionTime is greater than or equal to that of its parent.
        """
        while (k > 1):
            j = k >> 1
            if (self.queue[j].next_execution_time <= self.queue[k].next_execution_time):
                break
            tmp = self.queue[j]
            self.queue[j] = self.queue[k]
            self.queue[k] = tmp
            k = j

    def fix_down(self, k):
        """
         * Establishes the heap invariant (described above) in the subtree
         * rooted at k, which is assumed to satisfy the heap invariant except
         * possibly for node k itself (which may have a nextExecutionTime greater
         * than its children's).
         *
         * This method functions by "demoting" queue[k] down the hierarchy
         * (by swapping it with its smaller child) repeatedly until queue[k]'s
         * nextExecutionTime is less than or equal to those of its children.
        """
        j = k << 1
        while j <= self.qsize() and j > 0:
            if j < self.qsize() and \
                    self.queue[j].next_execution_time > self.queue[j+1].next_execution_time:
                j += 1
            if self.queue[k].next_execution_time <= self.queue[j].next_execution_time:
                break
            tmp = self.queue[j]
            self.queue[j] = self.queue[k]
            self.queue[k] = tmp
            k = j
            j = k << 1

    def heapify(self):
        """
         * Establishes the heap invariant (described above) in the entire tree,
         * assuming nothing about the order of the elements prior to the call.
        """
        for i in range(self.qsize()/2, 0, -1):
            self.fix_down(i)


class TimerThread(Thread):

    def __init__(self, queue):
        """
         * This flag is set to false by the reaper to inform us that there
         * are no more live references to our Timer object.  Once this flag
         * is true and there are no more tasks in our queue, there is no
         * work left for us to do, so we terminate gracefully.  Note that
         * this field is protected by queue's monitor!

         * Our Timer's queue.  We store this reference in preference to
         * a reference to the Timer so the reference graph remains acyclic.
         * Otherwise, the Timer would never be garbage-collected and this
         * thread would never go away.
        """
        Thread.__init__(self)
        self.newTasksMayBeScheduled = True
        self.queue = queue

    def run(self):
        try:
            self.main_loop()
        finally:
            self.__block.acquire()
            self.newTasksMayBeScheduled = False
            self.queue.clear()
            self.__block.release()


    def main_loop(self):
        """
         * The main timer loop.  (See class comment.)
        """
        while 1:
            try:
                task = None
                taskFired = False
                self.__block.acquire()
                    # Wait for queue to become non-empty
                while self.queue.is_empty() and self.newTasksMayBeScheduled:
                    self.queue.wait()
                    if self.queue.is_empty():
                        break # Queue is empty and will forever remain; die

                    # Queue nonempty; look at first evt and do the right thing

                    task = self.queue.get_min()
                    task.__block.acquire()

                    if task.state == TimerTask.CANCELLED:
                        self.queue.remove_min()
                        continue  #// No action required, poll queue again

                    currentTime = calendar.timegm(time.gmtime())
                    executionTime = task.nextExecutionTime
                    taskFired = executionTime <= currentTime
                    if taskFired:
                        if task.period == 0:  #// Non-repeating, remove
                            self.queue.remove_min()
                            task.state = TimerTask.EXECUTED
                        else:  #/ Repeating task, reschedule
                            self.queue.reschedule_min(currentTime   - task.period
                              if task.period < 0 else executionTime + task.period)

                    task.__block.release()
                    if not taskFired: # // Task hasn't yet fired; wait
                        self.queue.wait(executionTime - currentTime)
                self.__block.release()
                if taskFired:   #// Task fired; run it, holding no locks
                    task.run()
            except Exception, e:
                pass
