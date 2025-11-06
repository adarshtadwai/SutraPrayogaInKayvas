Currently for a given sloka we have below format where it contains the sloka and medata data described as follows :-

```
    {
      "loc": "1.2",
      "v": "यं सर्वशैलाः परिकल्प्य वत्सं मेरौ स्थिते दोग्धरि दोहदक्षे । भास्वन्ति रत्नानि महौषधीश्च पृथूपदिष्टां दुदुहुर्धरित्रीम् ॥",
      "sutra_sentences": [
        {
          "sutra": "2.1.49",
          "word": "",
          "sentence": "`पूर्वकालैकसर्वजरत्पुराणनवकेवलाः समानाधिकरणेन` इति समासः ।"
        },
        {
          "sutra": "2.3.37",
          "word": "",
          "sentence": "`यस्य च भावेन भावलक्षणम्` इति सप्तमी ।"
        },
        {
          "sutra": "1.4.51",
          "word": "",
          "sentence": "`अकथितं च` इति कर्मत्वम् ।"
        }
      ]
    },
```

This metaData is extracted from `In` folder's data.

Now your task is as follows :- 

- Using Claude sanskrit models you have to read the commentary and find the word which is described by the sutra and fill the word column
- Add One more field below `sentence` called `description` and write the extract the lines in 
commentary that sutra is talking about and fill it there.

Sources :-

- In folder's Json Files

To Write :-
- Enhance data in kumarasambhavam_Extract.json


Let me know if you have any futher queries.