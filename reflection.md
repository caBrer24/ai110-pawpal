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

Yes. Scheduler wasn't in the original design, it came in later as a way to store and access all the data in one place. Owner almost got cut since this started as a single-user app, but a scenario where two people share a pet made it worth keeping.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

Time of day, task duration, and priority. Time mattered most since the whole point is a daily schedule and knowing what to do when. Priority is visible but doesn't block anything, it's more of a heads-up for the owner.

**b. Tradeoffs**

Conflict detection only checks tasks for the same pet, not across pets. So if two pets have tasks at the same time, no warning shows. That's fine for now since one pet at a time is the more common scenario and cross-pet conflicts are a next iteration.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)? Brainstorming, but mostly for debugging since I got lost easily.
- What kinds of prompts or questions were most helpful? Explaining the situation, my thought process, the result I thought it was going to have and the actual result followed by: "Explain what I did wrong."

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is. AI suggested we used something else as a data storage other than the scheduler, although I did want to make it a class just to keep the difficulty at same level and not drift away from the project instructions. After all, I'm learning.
- How did you evaluate or verify what the AI suggested?
Initially I would just follow and try out the suggestions, but it was frustrating and had to go back many times when I saw that it was getting to a point where I didn't understand or would get lost in the structure AI was suggesting.
---

## 4. Testing and Verification

**a. What you tested**

Sorting, recurring task creation, conflict detection, filtering, and edge cases like scheduling a task in the past or marking an unknown task complete. These matter because they're where the logic could silently produce wrong results without crashing.

**b. Confidence**

Pretty confident for the scenarios it was built for. Next I'd test what happens when the same task gets marked complete twice, and what happens when two owners add conflicting tasks for the same shared pet.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with? The app is functional, minimalist/simple but functional. I'm just glad it ran

**b. What you would improve**

- If you had another iteration, what would you improve or redesign? a more complex schedule system with more considerations for a seamless integration with the owners actual schedule (maybe google calendar merge)

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
It's so easy to let AI do the work for you, but one must remember that AI knows how to do whatever we tell it to do alredy, we don't.