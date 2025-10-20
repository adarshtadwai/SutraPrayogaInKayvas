- Read all the files from from texts/extract folder and get an aggregated json file, write it to textAggregator/KavyaPrayogas.json. Code should lie in textAggregator/Aggregator.py
- It should be the aggregate  of all the entries in texts/extract files but in different order.

Format of Aggregated file should be as follows:
- Each entity should be keyed by sutraNumber ( take sutra  field in each file )
- Value should be a list of entities which has that sutra in them and each should have metaData as :-
{
            "word" : "", // currently empty String in our files
            "text": "रघुवंशम्", // should be the title of the text 
            "loc": "1.1", // should be the loc of the entity
            "url": "base_link + text",
            "ref": "माता च पिता च पितरौ, पिता मात्रा (अष्टाध्यायी १.२.७० ) इति द्वन्द्वैकशेषः ।"    // this field is sentence of entity

},

- Sort this file with sutraNumber