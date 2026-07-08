# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Owner should be able to add/remove a pet, schedule a walk, bath/grooming, see tasks for the day

- Briefly describe your initial UML design. 
Initially I thought about the main objects; Pet, Owner, Task
- What classes did you include, and what responsibilities did you assign to each?
**Pet**
Attributes: Name, breed, age, species
Responsibilities: get the task assigned to them, relate pet to owner 
**Task**
- Attributes: priority, kind, activity, duration, status, schedule_time
Responsibilities: mark a task done, check whether a task is pending, check whether a task is shared with more owners of the same pet
**Owner**
Attributes: name
Responsibilities: To add pets, to create tasks

**b. Design changes**

Yes. Two main changes happened. First, Scheduler was initially cut because it felt like overkill for the core features. It came back as the central data store once it became clear something needed to hold all owners, pets, and tasks and expose querying methods. Second, Owner was almost dropped for a single-user design, but a multi-owner scenario was a real requirement, so it stayed and Task got an optional owner_id to handle shared events.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers scheduled time (when the task is set to happen), duration in minutes, and priority (HIGH, MEDIUM, LOW). Time is treated as the primary constraint because the daily schedule view is chronological. Priority is visible in the display but does not currently filter tasks out. Duration is used by the conflict detector to check whether two tasks overlap, not just whether they share a start time.

**b. Tradeoffs**

The conflict detector checks for overlapping time windows (start time + duration) rather than exact start-time matches. For example, a 45-minute bath starting at 11:00 AM and a 30-minute vet visit starting at 11:20 AM are flagged as a conflict because their windows overlap, even though they don't start at the same moment.

This is a reasonable tradeoff for a pet care app because the owner physically cannot perform two tasks on the same pet simultaneously — overlapping durations are a real conflict, not just simultaneous start times. The limitation is that the check only applies to the same pet; two tasks for different pets at the same time are not flagged, even if the same owner would need to handle both. Cross-pet conflict detection is a natural next iteration.
---

## 3. AI Collaboration

**a. How you used AI**

AI was used in every phase: initial domain modeling, class skeleton generation, implementation of algorithms like conflict detection, and generating the test suite. The most useful prompts were the ones that asked for tradeoffs rather than just answers, like asking whether Scheduler should be a service or a data object. Questions that gave the AI context (attaching the relevant file) produced much better results than abstract questions.

**b. Judgment and verification**

Early on the AI suggested storing full Pet objects inside Owner (list[Pet]) rather than IDs. That was rejected because mixing object references and integer IDs in the same model creates inconsistency. The ID-based approach was chosen for all relationships so the model behaves the same way throughout. The suggestion was evaluated by thinking through what would happen if the same Pet object was updated in one place but a stale reference still existed elsewhere.

---

## 4. Testing and Verification

**a. What you tested**

The suite covers status changes, sorting correctness, recurring task creation for daily and weekly frequency, conflict detection for overlapping and exact-time cases, filtering by status and pet, and edge cases like a pet with no tasks or a task scheduled in the past. These are important because they cover the algorithmic logic that would silently produce wrong results rather than crash.

**b. Confidence**

4 out of 5. The unit tests cover the core logic well. The main gaps are integration tests that run the full owner to pet to task to schedule flow end to end, and the Streamlit layer which has no automated tests. Next edge cases to cover: adding the same pet twice, marking a task complete that has already been marked complete, and generating a schedule for an owner with no pets.

---

## 5. Reflection

**a. What went well**

The domain model. Taking the time to design the three-class structure and work through the relationships (especially the ID-based approach and the task_kind vs activity distinction) before writing any logic made the implementation straightforward. Most bugs were caught at the design stage rather than during coding.

**b. What you would improve**

Two things. First, add data persistence so the app does not reset when the browser tab closes. A simple JSON file export would be enough for this use case. Second, add cross-pet conflict detection so the scheduler can warn when the same owner has tasks for two different pets at the same time.

**c. Key takeaway**

AI is good at writing code once you know what you want, but it does not make the architectural calls for you. Every time the design drifted in a wrong direction (like removing Scheduler or using object references instead of IDs), it took a human judgment call to steer it back. Being the lead architect means deciding what to build and pushing back on suggestions that do not fit, not just accepting whatever the AI produces.
