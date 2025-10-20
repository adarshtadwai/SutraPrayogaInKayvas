Phase-1:
   - In texts/raghuvamsham.json, extract all entries which have a regex as (पा.3।3।19).
   - only take c,n,v and
   - take whole string which contains this regrex and to its left has danda and to its right have another danda ( single or double )
   - Write python script in scripts/AI_Generated/SutraPrayogaExtract.py
   - Write a document in Docs Folder of AI_Generated on what you have done

Phase-2:- Incorporating More intelligence to Sutra Structure.
   - Every sutra_sentence is now a list. I wanted to fine grain it as follows:
      - every sentence should now have two components in it.
         1. sutra ( in form 3.1.124)
         2. sentence 
      - Enhancing sutra_sentences.
         1. ( remove (पा.x।x।x) from sentence )
         2. I see some sentenses ( like like 57)। ) are present. [ here before sutra there is a single danda but it is included ]
         3. If the text is small in sentence then go for one danda before instead of current.
   - Include a sepereate component to do phase2 and integrate it with current python script
         
