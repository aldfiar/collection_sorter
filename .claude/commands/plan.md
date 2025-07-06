Write a implementation plan fo feature $ARGUMENTS.
Follow this steps:
1. Understand the feature 
2. Draft a detailed, step-by-step blueprint for implementing this feature. Break it down into small, iterative chunks that build on each other. Look at these chunks and then go another round to break it into small steps. review the results and make sure that the steps are small enough to be implemented safely. Iterate until you feel that the steps are right sized for this project.
3. From here you should have the foundation to provide a series of prompts for a code-generation LLM that will implement each step. Prioritize best practices, and incremental progress, ensuring no big jumps in complexity at any stage. Make sure that each prompt builds on the previous prompts, and ends with wiring things together. There should be no hanging or orphaned code that isn't integrated into a previous step.
4. Make sure and separate each prompt section. Use markdown. Each prompt should be tagged as text using code tags. The goal is to output prompts, but context, etc is important as well.
5. Store the plan in docs/$feature_name/plan.md. Also create a docs/$feature_name/todo.md to keep state.
