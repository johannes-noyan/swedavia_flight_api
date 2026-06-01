##################################################
🧩 4. Reverse Engineer a Result

    Preparation: Recreate an application with GenAI(this will be provided by a Najmaddin).
    Goal: You are given an finished application. You figure out what code made it.

##################################################
✅ Step-by-Step:

    🟣 Step 1: Look at the application

        Example: an API or a database.


    🟣 Step 2: Ask Questions

        What kind of data is this?
        What could have created this?
        Use GenAI like Lovable or V0 


    🟣 Step 3: Guess the Inputs

        What inputs would you need to get this result?


    🟣 Step 4: Guess the Process

        What functions or logic might build this?
            Example:
                You see a JSON like:
                    { "user": "Anna",
                    "score": 87
                    }

        You guess:

            1. A user typed their name
            2. A test was taken
            3. The score was calculated and saved


    🟣 Step 5: Sketch the Steps

        Write a fake function like:
            def get_score(user_answers):
                # Compare to correct answers
                # Return score


    🟣 Step 6: Try Building It

        Can you make an application that gives similar output?

##################################################

💡 Tips:

    Work backwards.
    Use logic and clues in the data.
    Like being a detective! 🕵🏻‍♀️👣

##################################################
APL-project 2026                              
