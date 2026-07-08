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

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
   
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

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with? The app is functional, minimalist/simple but functional. I'm just glad it ran

**b. What you would improve**

- If you had another iteration, what would you improve or redesign? a more complex schedule system with more considerations for a seamless integration with the owners actual schedule (maybe google calendar merge)

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
It's so easy to let AI do the work for you, but one must remember that AI knows how to do whatever we tell it to do alredy, we don't.