import json
import nltk
from nltk.corpus import wordnet as wn
stringGiven = [[["China", "(\"Nigeria, China Strengthen Cooperation on Energy and Security\",haberler.com,Turkey)"], ["China", "(\"Volkswagen cuts own-brand sales by 1.4 percent in 2024\",bloomberght.com,Turkey)"], ["China", "(\"Scandal over Chinese espionage case in Germany! 3 Germans on trial\",sozcu.com.tr,Turkey)"], ["China", "(\"Germany puts Chinese agents on trial\",odatv.com,Turkey)"], ["China", "(\"NASA says China's project could slow down Earth's rotation\",odatv.com,Turkey)"], ["China", "(\"Volkswagen's vehicle deliveries fall in 2024\",milliyet.com.tr,Turkey)"], ["China", "(\"UN Announces Global Economic Growth Forecasts\",haberler.com,Turkey)"], ["China", "(\"Reaction to Tanju \u00d6zcana is growing like an avalanche: Workers have not received their pay for 3 months... Reaction to the process\",yeniakit.com.tr,Turkey)"], ["China", "(\"New POCO X7 Series Launched in Turkey: Featured Features and Price Here!\",tamindir.com,Turkey)"], ["China", "(\"EU Chamber of Commerce: Forced \"\"isolation\"\" of foreign companies in China brings double risks | International\",cna.com.tw,Taiwan)"], ["China", "(\"You are in me and I am in you Ouyang Yujing: China's investment in Malaysia has grown by leaps and bounds | China Press\",chinapress.com.my,Malaysia)"], ["China", "(\"Panama refutes Trump's allegations \u2013 DW \u2013 January 9, 2025\",dw.com,Germany)"], ["China", "(\"Malaysia-China trade volume is expected to break the 200 billion mark. Ouyang Yujing: China continues to be Malaysia's largest trading partner | Domestic\",orientaldaily.com.my,Malaysia)"], ["China", "(\"UK finances raise concerns; MPs urge finance minister to cancel visit to China | International\",cna.com.tw,Taiwan)"], ["China", "(\"Loke Siew Fook: Returning to Jit Sin Secondary School where he once taught, the Prime Minister will hand over funding for 63 independent Chinese secondary schools on the 11th\",enanyang.my,Malaysia)"], ["China", "(\"Not just one person, Wu Nai-jen's extravagant banquet was inspected 5 times in one evening | Wu Nai-jen's extravagant banquet caused controversy | News\",udn.com,Taiwan)"], ["China", "(\"Negotiations between the ruling and opposition parties extend the \"\"double hegemony\"\" between Ko Chien-ming and Han Kuo-yu | The issue of impeachment continues to rage | News\",udn.com,Taiwan)"], ["China", "(\"Lai Ching-te's old article was dug up, praising Wu Nai-ren \"\"Meng Changjun\"\": Treating money as if it were nothing else - Politics\",chinatimes.com,Taiwan)"], ["China", "(\"Jiang Qichen rushes to sign up for Trump's congratulatory delegation. Legislative Yuan official: We have discussed this with the Ministry of Foreign Affairs | Politics\",cna.com.tw,Taiwan)"], ["China", "(\"Kaohsiung's 113-year investment promotion exceeded NT$100 billion, and private investment hit a new high | Politics\",newtalk.tw,Taiwan)"], ["China", "(\"The Spring Festival new banknote exchange starts on 1/20. Banks issue wealth water vaults to accumulate wealth\uff5cKayou News Network\",cardu.com.tw,Taiwan)"], ["China", "(\"Exclusive / Wu Nai-ren and prosecutors were exposed to have dinner at a 60,000 star restaurant, 5 prosecutors were present | Wu Nai-ren's extravagant banquet caused controversy | News\",udn.com,Taiwan)"], ["China", "(\"\"\"Big Short Selling\"\" The real Berry quietly increased his stake in Alibaba and JD.com. What did he see? | Global Finance | Global\",udn.com,Taiwan)"], ["China", "(\"Pope Francis receives envoys from diplomatic allies. Taiwan's ambassador extends greetings on behalf of President Lai and prays for peace | Politics\",cna.com.tw,Taiwan)"], ["China", "(\"Vietnam's trade surplus with the US soars, potential tariff risks increase - Finance\",chinatimes.com,Taiwan)"], ["China", "(\"Visit to Kaohsiung Postal Museum Xu Zhijie hopes to boost the development of the new railway station business district | Life\",newtalk.tw,Taiwan)"], ["China", "(\"This year's total health insurance amount is a record high of 928.6 billion yuan. Civil groups are worried about the increase in premiums | Life News | Life\",udn.com,Taiwan)"], ["China", "(\"Infusion stock is running low, even major hospitals sound the alarm | Life News | Life\",udn.com,Taiwan)"], ["China", "(\"UN predicts world economic growth to remain at 2 . 8 % in 2025\",straitstimes.com,Singapore)"], ["China", "(\"China inflation hit nine - month low in December\",thedailystar.net,Bangladesh)"], ["China", "(\"POLL : Should Rachel Reeves be in China while the pound plummets ? | Politics | News\",express.co.uk,\"United Kingdom\")"], ["China", "(\"UN predicts world economic growth at subdued 2 . 8 % in 2025\",apnews.com,\"United States\")"], ["China", "(\"UN predicts world economic growth at subdued 2 . 8 % in 2025 \u2013 Winnipeg Free Press\",winnipegfreepress.com,Canada)"], ["China", "(\"HMPV virus symptoms : What is human metapneumovirus ? China steps up monitoring amid new outbreak\",independent.co.uk,\"United Kingdom\")"], ["China", "(\"Chinese actor Wang Xing says he was trafficked to Myanmar\",independent.co.uk,\"United Kingdom\")"], ["China", "(\"What is the state of trade relations between EU and China ? \",euronews.com,\"United States\")"], ["China", "(\"Dutch Holiday Fair highlights China as top travel destination\",thestar.com.my,Malaysia)"], ["China", "(\"Amid Subdued Global Growth , East and South Asia Emerge as Pillars of Resilience : UN Report\",businesstoday.in,India)"], ["China", "(\"EU companies forced to  silo  operations in China , harming competitiveness , report finds\",euronews.com,\"United States\")"], ["China", "(\"Trilateral phone call set among Marcos Jr ., biden , Ishiba\",philstar.com,Philippines)"], ["China", "(\"How worried should you be about the HMPV outbreak in China ? Experts weigh in\",independent.co.uk,\"United Kingdom\")"], ["China", "(\"Green development - key focus of China - Africa cooperation : spokesperson\",news.az,Azerbaijan)"], ["China", "(\"EXPLAINER | What China mega dam project means for India - India News\",financialexpress.com,India)"], ["China", "(\"US aircraft carrier deployed to South China Sea\",philstar.com,Philippines)"], ["China", "(\"China Coal Demand and Production Will Continue to Grow in 2025\",oilprice.com,\"United States\")"], ["China", "(\" ,:  Trump is a businessman and wants deals  \",zeit.de,Germany)"], ["China", "(\"Germany : Three indicted on charges of spying for China \u2013 DW \u2013 01 / 09 / 2025\",dw.com,Germany)"], ["China", "(\"Anne Hathaway Is a Princess in This Sculptural Gold Gown\",harpersbazaar.com,\"United States\")"], ["China", "(\"China proposed export ban a  wake - up call  for Western battery supply chains : First Phosphate CEO\",proactiveinvestors.com,\"United States\")"], ["China", "(\"Opinion - The risk of nuclear war continues to rise\",yahoo.com,\"United States\")"], ["China", "(\"The risk of nuclear war continues to rise\",thehill.com,\"United States\")"], ["China", "(\"Iron Ore Prices Face Downward Pressure in 2025\",oilprice.com,\"United States\")"], ["China", "(\"Sensodetect announces license revenue from joint venture in China\",marketscreener.com,\"\")"], ["China", "(\"So Trump wants Greenland ? Dont laugh , America been here before\",watoday.com.au,Australia)"], ["China", "(\"Trump Energy Plan Will Avoid Europe Energy Disaster | The Heritage Foundation\",heritage.org,\"United States\")"], ["China", "(\"Five climate change stories to keep an eye on this year\",phys.org,\"United States\")"], ["China", "(\"Mpox In China : Cluster Of New Mutated Strain Detected ; Know Symptoms And Complication\",ndtv.com,India)"], ["China", "(\"Is There A New Cluster Outbreak Of Mpox 1b Subclade In China ? \",thehealthsite.com,India)"], ["China", "(\"Taiwan records second highest year of exports in 2024\",focustaiwan.tw,Taiwan)"], ["China", "(\"Nvidia and AI Chip Stocks Brace for Impact as Biden Administration Considers New China Export Ban : Report - NVIDIA ( NASDAQ : NVDA ) \",benzinga.com,\"United States\")"], ["China", "(\"China Just Launched The World Fastest High - Speed Train \u2013 Here the Exact Date You Can Ride It\",timeout.com,\"United Kingdom\")"], ["China", "(\"In Yemen , China Has Quietly Helped the Houthi Militants\",nationalinterest.org,\"United States\")"], ["China", "(\"Biden Final Chip Curbs Set To Shake AI Markets : 10 ETFs With High Stakes In Nvidia , AMD - Advanced Micro Devices ( NASDAQ : AMD ), AOT Growth and Innovation ETF ( NASDAQ : AOTG ) \",benzinga.com,\"United States\")"], ["China", "(\"TikTok Potential U . S . Ban : What Are Trump Options ? \",newsweek.com,\"United States\")"], ["China", "(\"US seizure of Greenland is  not going to happen , says David Lammy | David Lammy\",theguardian.com,\"United Kingdom\")"], ["China", "(\"The Navy thinking about China plan for Taiwan - Washington Examiner\",washingtonexaminer.com,\"United States\")"], ["China", "(\"Rachel Reeves faces claims of  fleeing to China  amid concerns over united kingdom borrowing\",lynnnews.co.uk,\"United Kingdom\")"], ["China", "(\"PRESS : Shein London listing could be completed by Easter - Reuters\",lse.co.uk,\"United Kingdom\")"], ["China", "(\"Chinese Hackers Targeted Japan by Exploiting VPN Flaws\",pcmag.com,\"United States\")"], ["China", "(\"2 - GW Gas - Fired Plant With GE Vernova Turbines Now Online in China\",yahoo.com,\"United States\")"], ["China", "(\"Japanese Crime Boss Pleads Guilty in Plot To Sell Nuclear Material To Iran\",oilprice.com,\"United States\")"], ["China", "(\"Indonesian President plan to club visits to India , Pakistan puts Delhi at unease amid Brahmos negotiations\",deccanherald.com,India)"], ["China", "(\"US ships getting preferential rates  will lead to chao : Panama Canal administrator\",prokerala.com,India)"], ["China", "(\"The West Regains Ground In Iraq As BP Finalises Terms On Huge Kirkuk Oil Project\",oilprice.com,\"United States\")"], ["China", "(\"TikTok says it plans to shut down site unless Supreme Court strikes down law forcing it to sell\",cbsnews.com,\"United States\")"], ["China", "(\"Afghanistan Untapped Economic Potential Hindered By Limited Trade and Investment , Says UN Expert\",khaama.com,Afghanistan)"], ["China", "(\"HMPV cases rise in united kingdom as doctors call  for more information  from China\",birminghammail.co.uk,\"United Kingdom\")"], ["China", "(\"TikTok Fate Arrives At Supreme Court In Collision Of Free Speech And National Security \u2013 The Yeshiva World\",theyeshivaworld.com,\"United States\")"], ["China", "(\"Opinion - Surprise ! Why Europe could end up as one of Trump biggest problems overseas\",yahoo.com,\"United States\")"], ["China", "(\"UAE : Lower petrol prices to continue as oil glut looms\",khaleejtimes.com,\"United Arab Emirates\")"], ["China", "(\"Uncertainty Over Trump Electric Vehicle Policies Clouds 2025 Forecast For Carmakers \u2013 The Yeshiva World\",theyeshivaworld.com,\"United States\")"], ["China", "(\"Will Brent Break $80 ? Winter Demand , Offshore Drilling , and Technicals in Focus\",investing.com,\"United States\")"], ["China", "(\"VW strains to hit EU emission targets as EV deliveries tumble\",irishtimes.com,Ireland)"], ["China", "(\"Uncertainty over Trump electric vehicle policies clouds 2025 forecast for carmakers\",sandiegouniontribune.com,\"United States\")"], ["China", "(\"India is a  significant regional partner : Taliban\",bdnews24.com,Bangladesh)"], ["China", "(\"Sikkim issues health advisory for HMPV\",prokerala.com,India)"], ["China", "(\"80 - Year - Old Ahmedabad Man Tested Positive For HMPV Virus ; Second Case Reported In Gujarat\",oneindia.com,India)"], ["China", "(\"Zobels , Yuchengcos launch new medical school\",philstar.com,Philippines)"], ["China", "(\"BCC Research LLC : Transforming Healthcare : AI in Diagnostics Market to See 27 . 6 % CAGR Growth\",finanznachrichten.de,Germany)"], ["China", "(\"What it will take for TikTok to survive in the US\",theverge.com,\"United States\")"], ["China", "(\"USTR  Notorious Markets List  spotlights illicit online pharmacies and risk of counterfeit medicines\",thehindubusinessline.com,India)"], ["China", "(\"China Development Bank Releases $255 Million Loan for Rail Project in Nigeria\",legit.ng,\"\")"], ["China", "(\"The truth about the much - hyped  world longest train journey  \",watoday.com.au,Australia)"], ["China", "(\"TikTok ban solution ?  Shark Tank  Kevin OLeary and billionaire Frank McCourt want to buy the app\",cnn.com,\"United States\")"], ["China", "(\"Kevin OLeary wants to buy TikTok , but it not for sale\",ctvnews.ca,Canada)"], ["China", "(\"TikTok is about to have its day at the Supreme Court . Here what to know as it fights a U . S . ban\",yahoo.com,\"United States\")"], ["China", "(\"Walmart CEO Doug McMillon meets with Trump on trade relations , investing in US\",foxbusiness.com,\"United States\")"], ["China", "(\"Canada tariffs on Chinese EVs pose quandary for next PM\",chathamdailynews.ca,Canada)"], ["China", "(\"Exports grow 9 . 2 percent ahead of LNY\",taipeitimes.com,Taiwan)"], ["China", "(\"Donald Trump , the  America First  candidate , has a new preoccupation : Imperialism\",pressdemocrat.com,\"United States\")"], ["China", "(\"  What Are You Complaining About ?: Economists Assail Trump Canada Trade Math\",yahoo.com,\"United States\")"], ["China", "(\"Phl - Korea FTA and US tariffs\",philstar.com,Philippines)"], ["China", "(\"US  Notorious Market Report Warns Of Risks From Online Pharmacies \u2013 The Yeshiva World\",theyeshivaworld.com,\"United States\")"], ["China", "(\"Latest TikTok Ban Updates : Here What We Know As Deadline Nears\",forbes.com,\"United States\")"], ["China", "(\"An army airstrike on a village in western Myanmar has killed at least 40 people , reports say\",panow.com,Canada)"], ["China", "(\"Trade deficit narrows to $4 . 8 billion in November\",philstar.com,Philippines)"], ["China", "(\"US trade officials highlight risk of using online pharmacies\",thehill.com,\"United States\")"], ["China", "(\"Pinkus in an interview with haqqin.az: \"\"Trump will tell Azerbaijan: if you help me, I will definitely help you\"\"\",haqqin.az,Azerbaijan)"], ["China", "(\"New BMW X3 and Toyota Highlander go on sale in Russia. Prices and trim levels :: Autonews\",autonews.ru,Russia)"], ["China", "(\"Why is Greenland important and why does Trump need it? - BBC News Russian Service\",bbc.com,\"United Kingdom\")"], ["China", "(\"China's Largest Pumped Storage Power Plant Fengning Launched\",focus.ua,Ukraine)"], ["China", "(\"School in China - Chinese parents hire couriers\",focus.ua,Ukraine)"], ["China", "(\"Fire Swallowing - Unreasonable Practices Used on People in China\",focus.ua,Ukraine)"], ["China", "(\"Flight from China to Moscow landed in Krasnoyarsk due to illness of a passenger\",tass.ru,Russia)"], ["China", "(\"China has forged! Counterfeit Russian goods found in the Celestial Empire\",aif.ru,Russia)"], ["China", "(\"Zeekr 007 GT wagon shown in China\",autoreview.ru,Russia)"], ["China", "(\"Tensions Rise Between China and Canada - Arguments of the Week\",argumenti.ru,Russia)"], ["China", "(\"Trump's Harmful Weapon\",charter97.org,Belarus)"], ["China", "(\"Sergunina: Representatives of 10 countries are interested in joint film projects with Moscow\",argumenti.ru,Russia)"], ["China", "(\"Updated Tesla Model Y Released into Snow\",motor.ru,Russia)"], ["China", "(\"US News - Are Trump's Plans for Greenland, Canada and Panama Serious?\",glavred.info,Ukraine)"], ["China", "(\"Metals Melt Ice. Economist Litvinenko Explains Why Trump Needs Greenland\",aif.ru,Russia)"], ["China", "(\"Belarus presidential candidate doesn't believe Trump's words about peace in Ukraine\",ria.ru,Russia)"], ["China", "(\"Vucevic: Serbia expects start of strategic dialogue with US and rapprochement in military-industrial complex\",tass.ru,Russia)"], ["China", "(\"Five Future Scenarios: Where AI Will Lead the World in 2025\",securitylab.ru,Russia)"], ["China", "(\"Shanghai Organizes Inspection of 47 Shops Selling Fake Russian Goods\",vesti.ru,Russia)"], ["China", "(\"A sedan priced at 2,18 million rubles can be purchased with a big discount, we tell you where\",zr.ru,Russia)"], ["China", "(\"Choosing in favor of China: Serbia suddenly terminates a number of military deals with Russia\",focus.ua,Ukraine)"], ["China", "(\"Trump's Scandalous Statements - What Does the New US President Want?\",24tv.ua,Ukraine)"], ["China", "(\"Investigation launched in China into falling prices of Chinese beef\",farmer.pl,Poland)"], ["China", "(\"Denmark: Greenland proposes cooperation with the United States in the extraction of critical raw materials\",wnp.pl,Poland)"], ["China", "(\"UN report: The Greek economy is \"\"running\"\" at a rate twice that of the EU - Estimates for the 3-year period\",inewsgr.com,Greece)"], ["China", "(\"Alarm over mpox in China - 5 cases of the new clade 1b variant recorded\",protothema.gr,Greece)"], ["China", "(\"China: Beijing announces five cases of new variant of mpox\",inewsgr.com,Greece)"], ["China", "(\"Why G. Papandreou did not go to the funeral of K. Simitis\",inewsgr.com,Greece)"], ["China", "(\"Britain: Markets and Musk \"\"saw\"\" Starmer's chair\",inewsgr.com,Greece)"], ["China", "(\"Why George Papandreou did not appear at Simitis' funeral\",inewsgr.com,Greece)"], ["China", "(\"George Papandreou: Why he did not attend the funeral of Costas Simitis\",inewsgr.com,Greece)"], ["China", "(\"Beijing: EU imposes unfair trade barriers on Chinese companies\",lrt.lt,Lithuania)"], ["China", "(\"German prosecutors indict three people on suspicion of spying for China\",diena.lt,Lithuania)"], ["China", "(\"Deflation Alert in China Markets warn Beijing\",zazoom.it,Italy)"], ["China", "(\"Volkswagen Car Sales Down in 2024, China Weighs In - News\",ansa.it,Italy)"], ["China", "(\"Hmpv virus is in Greece, first patient admitted to intensive care: daughter had gone to China. Symptoms (confusable) and contagion\",ilmessaggero.it,Italy)"], ["China", "(\"Trump storms the Panama Canal, the plan to prevent it from falling into China's hands\",affaritaliani.it,Italy)"], ["China", "(\"Assopellettieri: - 9.7% in export value 9 months 2024, - 28% China sales III quarter.\",borsaitaliana.it,Italy)"], ["China", "(\"Realme 14 Pro+ is official with Android 15 and a 6,000 mAh battery\",tuttoandroid.net,Italy)"], ["China", "(\"Fight for the Arctic: Trump parks himself in Greenland, Peskov responds harshly\",secoloditalia.it,Italy)"], ["China", "(\"Stock Market: Europe closes on the rise, Milan (+0.59%) returns to May highs\",ilsole24ore.com,Italy)"], ["China", "(\"Bisagno Drainage Plant, Penalty Coming for Delayed Mole in Genoa - Primocanale . it\",primocanale.it,Italy)"], ["China", "(\"China to further ease investment restrictions for foreign firms\",zazoom.it,Italy)"], ["China", "(\"China | Shandong Boshan exhibits colored enamel handicrafts\",zazoom.it,Italy)"], ["China", "(\"China | Beijing Book Fair kicks off with 400,000 titles on display\",zazoom.it,Italy)"], ["China", "(\"Chinese New Year, concert at the Civic on January 13th\",cittadellaspezia.com,Italy)"], ["China", "(\"Hmpv virus is in Greece, first patient in intensive care: checks start. Symptoms (mistakable) and how he was infected\",ilmessaggero.it,Italy)"], ["China", "(\"3500 jobs at risk in South African steel company - Africa\",ansa.it,Italy)"], ["China", "(\"In December 2024, Germany accused three of its citizens of spying for China\",dennikn.sk,\"Slovak Republic\")"], ["China", "(\"German prosecutors charge three people with spying for China\",aktuality.sk,\"Slovak Republic\")"], ["China", "(\"Tax increases, another round of price increases, or an incompetent EU. What awaits Slovaks in 2025?\",aktuality.sk,\"Slovak Republic\")"], ["China", "(\"Carter's final farewell at his American funeral, attended by former presidents: Chunichi Shimbun Web\",chunichi.co.jp,Japan)"], ["China", "(\"Battle of the Chinese Dragon.. Why does Trump insist on buying Greenland?\",dostor.org,Egypt)"], ["China", "(\"American Institute: All factors are favorable for opening an American consulate in Laayoune\",akhbarona.com,Morocco)"], ["China", "(\"Fire-eating in China is an unfounded practice used on people\",focus.ua,Ukraine)"], ["China", "(\"The matter will not be limited to Canada, Greenland and the Panama Canal. The battle is for dominance for 100 years.\",gordonua.com,Ukraine)"], ["China", "(\"Russia to begin mass production of Marker ground drone with drone swarm and Kornet missiles\",focus.ua,Ukraine)"], ["China", "(\"Choosing China: Serbia suddenly breaks off a series of military agreements with Russia\",focus.ua,Ukraine)"], ["China", "(\"The media has learned who Trump invited to his inauguration and whether Putin is on the list\",gordonua.com,Ukraine)"], ["China", "(\"Volkswagen: sales decline in 2024, particularly in China\",rfj.ch,Switzerland)"], ["China", "(\"\"\"Mongolia becomes a new partner of France, but risks exist\"\"\",causeur.fr,France)"], ["China", "(\"Human Metapneumovirus: 8 questions about the MPVh that is raging in China\",lindependant.fr,France)"], ["China", "(\"Donald Trump could cause headaches for investors in Europe and China\",vg.hu,Hungary)"], ["China", "(\"According to the UN, the world economy will grow by 2.8 percent this year\",vg.hu,Hungary)"], ["China", "(\"Fredly owns over 15 percent of Spetalen - company\",e24.no,Norway)"], ["China", "(\"Believes Norway must negotiate directly with Trump\",e24.no,Norway)"], ["China", "(\"Alternative to the West: BRICS - Alliance around China and Russia gains power\",wa.de,Germany)"], ["China", "(\"Suspected of espionage for China: Federal Prosecutor\u2019s Office charges three Germans\",lvz.de,Germany)"], ["China", "(\"Scientific espionage for China? Prosecution in D\u00fcsseldorf\",freiepresse.de,Germany)"], ["China", "(\"Scientific espionage for China? Indictment in D\u00fcsseldorf - Politics\",pz-news.de,Germany)"], ["China", "(\"Great news for those looking to buy a mobile phone\",dailyaaj.com.pk,Pakistan)"]]]


if __name__ == "__main__":
    jsonInfo = json.dumps(stringGiven)

    loadJson = json.loads(jsonInfo)
    loadJson = loadJson[0]
    allWords = {}

    tokenizer = nltk.NLTKWordTokenizer()

    for i in range(len(loadJson)):
        processed = loadJson[i][1].split('"')
        for word in (tokenizer.tokenize(processed[1])):
            if word == "Greenland":
                print(loadJson[i])
            if allWords.get(word) == None:   
                allWords[word] = 1
            else:
                allWords[word] += 1

    maxWord = [[0,"0"]] * 300

    for key in allWords:
        count = allWords[key]
        if count >= min(list(zip(*maxWord))[0]):
            maxWord.append([count,key])
            index = maxWord.index(min(maxWord))
            del maxWord[index]

    finalDict = {}

    i = 0
    for w in list(zip(*maxWord))[1]:
        try:
            tmp = wn.synsets(w)[0].pos()
        except:
            tmp = "failed"
        if tmp == "n" and len(w) >= 2:
            finalDict[w] = maxWord[i][0]
        i += 1

    finalDict = {k: v for k, v in sorted(finalDict.items(), key=lambda item: item[1])}    

    print(finalDict)