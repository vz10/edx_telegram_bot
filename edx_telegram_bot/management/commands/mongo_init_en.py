# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from ...bot_mongo import BotMongo

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('course_name', nargs='+', type=str)

    def handle(self, *args, **options):
        self.course_key = options['course_name'][0]
        self.mongo_client = BotMongo(database='bot', collection=self.course_key)
        # Initial fixtures for mongo collection
        # Introduction step
        self.mongo_client.send({'Problem': """
*Assist Peter the Raccoon in Reforming His Zoo*
Peter the Raccoon was one of the “Mezhlissya” Zoo inhabitants.
He became the leader of the herd after Viktor the Boar fled.
A couple of months prior to this, the previous leader ran away to the nearby “Northern Wasteland” zoo, as he became too greedy and the animals kicked him away.
The zoo was left in pitiable condition, as Victor the Boar took almost all food with him, also annexing the southern part of the zoo in the process.
                                            """,
                               'Right_answer': "I'm ready!",
                               'Wrong_answers': [],
                               'Positive_answer': "*You are great, let's go.*",
                               'Order': 0,
                               'Next_step_order': 1})
        # Step 1
        self.mongo_client.send({'Problem': '''
Peter offered himself as the new zoo leader. He said there was no other animal able to reform the zoo.
***Are raccoons intelligent? Will Peter be able to reform the zoo as he promised?***
                                            ''',
                                'Wrong_answers': ['Nope, why should they? Not smarter than a rock.',
                                                  'Smart enough to not being caught while stealing someone’s garbage.'],
                                'Right_answer': 'Only smart raccoons live on our planet',
                                'Video_url': 'https://dl.dropboxusercontent.com/u/20018982/SZqamfJ.mp4',
                                'Theoretical_part': '''
High IQ level of raccoons is one of the most amazing raccoon facts in this list. According to experts, raccoons scored very high on the mammal IQ level test. They were found to be more intelligent than cats. They have amazing skills of opening locks and closed doors. In a study, from a total of 13 locks, raccoons were able to open 11 locks. They were also able to memorize the combination which suggests raccoons were intelligent enough to understand the complex mechanism of locks.Raccoons have amazing and quick learning skills. They can memorize the solution of complex mechanism for three years and they can also identify and differentiate between different symbols.Moreover, smartest raccoons (with IQ higher than an average monkey has) work for Raccoon Gang :D
                                            ''',
                                'Negative_answer': "Looks like raccoon are smarter than you think :)",
                                'Positive_answer': "*Hm. You should send us your CV :)*",
                                'Order': 1,
                                'Next_step_order': 2})
        # Step 2
        self.mongo_client.send({'Problem': '''
After some debates and consideration, the animals gave Peter the Raccoon vote of confidence for the quantity of years equal to the amount of fingers on his paw.
***How many fingers do raccoons have?***
                                            ''',
                                'Wrong_answers': ['Four', 'Depending on the season'],
                                'Right_answer': 'Five',
                                'Theoretical_part': "A raccoon’s hands are so nimble they can unlace a shoe, unlatch a cage and deftly retrieve coins as thin as dimes from your shirt pocket.",
                                'Image_url': 'https://dl.dropboxusercontent.com/u/20018982/racoon_pow.jpg',
                                'Negative_answer': "Hm, raccoons are closer to humans in case of body structure btw;)",
                                'Positive_answer': "That was easy. Don't be so happy. ;)",
                                'Order': 2,
                                'Next_step_order': 3})
        # Step 3
        self.mongo_client.send({'Problem': '''
Peter received help from many friends, one of whom were Senya the Rabbit. Senya liked carrots very much. However, there weren’t much carrots left in the zoo, as their garden beds were destroyed by Victor the Boar and his herd of swines while they were running away. The animals decided to borrow some carrots from the other zoos. But carrot diet is obviously not enough!
*What does raccoon eat?*
                                            ''',
                                'Wrong_answers': ['Drink beer and eat chips', 'Drink beer and eat meat', 'Pizza and burgers'],
                                'Right_answer': 'All in list above and anything else',
                                'Theoretical_part': "They are true omnivores and are opportunistic in their diet. They will eat fruit, insects, berries, nuts, eggs, small rodents, grapes, corn, crabs, crayfish and anything edible you may have left in the backyard.",
                                'Image_url': 'https://dl.dropboxusercontent.com/u/20018982/raccoon_food.jpg',
                                'Video_url': 'https://dl.dropboxusercontent.com/u/20018982/raccoon.mp4',
                                'Negative_answer': "You are narrow minded.",
                                'Positive_answer': "Oh yes, I'm lovin' it, give me more of all this yummy.",
                                'Order': 3,
                                'Next_step_order': 4})
        # Step 4
        self.mongo_client.send({'Problem': '''
Nosey magpies found out that Peter the Raccoon had several visits to the neighboring zoo and washed some carrot in their pond. Allegedly, he washed quite a lot of them, because the water there is cloudy and no one can tell how many carrots are lying on the pond’s bottom. Despite trying to keep things secret, Peter was busted along with the leader of the “Northern Wasteland” zoo - Vova the Poodle.
*Do raccoons truly wash their food?*
                                    ''',
                                'Wrong_answers': ['Yes, they are doing that everytime they eat.'],
                                'Right_answer': 'Nope, they don’t.',
                                'Theoretical_part': 'It was once thought that raccoons washed their food. They do not. Raccoons have a highly sensitive sense of touch which water helps to enhance. Even when water is unavailable, raccoons will use the same motions while they manipulate their food or objects they are interested in. This tactile experience gives the raccoon a better sense of what it will be eating. It is as if they "see" with their hands. Raccoons have bad eyesight and are color blind, but have great hearing and a great sense of smell.',
                                'Video_url': 'https://dl.dropboxusercontent.com/u/20018982/d0cEd2Q.mp4',
                                'Negative_answer': "Yeah, everybody thinks so...",
                                'Positive_answer': "Maybe you have one at home, huh?",
                                'Order': 4,
                                'Next_step_order': 5})
        # Step 5
        self.mongo_client.send({'Problem': '''
The animals began to become disappointed with Peter’s rule. Will he have enough time to rectify the mess in the zoo?
*For how long do the raccoons usually live? *
                                    ''',
                                'Wrong_answers': ['Less than 5 years', 'Up to 10 years', 'Up to 15 years'],
                                'Right_answer': 'More than 15 years',
                                'Theoretical_part': "Raccoons may live up to 16 years in the wild, but most don't make it past their second year. If they survive their youth, raccoons may live an average of 5 years in the wild. The primary causes of death are humans (hunting, trapping, cars) and malnutrition. A captive animal was recorded living for 21 years.",
                                'Image_url': 'https://dl.dropboxusercontent.com/u/20018982/raccoon-cubs.jpg',
                                'Negative_answer': "Yo, raccoons live longer than you think!",
                                'Positive_answer': "Great begging!",
                                'Order': 5,
                                'Next_step_order': 6})
        # Step 6
        self.mongo_client.send({'Problem': '''
While reforming the zoo, Peter the Raccoon has to chase boars and other animals, as many of them know about secret stashes of carrots. However, some animals run pretty fast. Will Peter be able to chase them down?
*How fast can raccoons run?*
                                    ''',
                                'Wrong_answers': ['Up to 35 mph', 'More than 50 mph'],
                                'Right_answer': 'Less than 20 mph',
                                'Theoretical_part': "Their common gait is a shuffle like walk, however, they are able to reach speeds of 15 miles per hour on the ground. Raccoons climb with great agility and are not bothered by a drop of 35 to 40 feet. As well as being excellent climbers, raccoons are strong swimmers, although they may be reluctant to do so. Without waterproof fur, swimming forces them to take on extra weight. Raccoons don't travel any farther than necessary; they travel only far enough to meet the demands of their appetites. In a Virginia mountain hollow, resident raccoons traveled between 0.75 and 2.5 km per night, with males traveling slightly farther during fall, winter, and spring, and females traveling longer during summer, when they are foraging with and for their young.",
                                'Image_url': 'https://dl.dropboxusercontent.com/u/20018982/raccoon-cubs.jpg',
                                'Negative_answer': "Really? Have you ever tried to run more than 5 mph? It is hard!",
                                'Positive_answer': "You are right. There is no need to run quicker when you are dat awesome :)",
                                'Order': 6,
                                'Next_step_order': 7})
        # Step 7
        self.mongo_client.send({'Problem': '''
Peter the Raccoon was barely able to do anything, but he received help from true friends!.
*Are raccoons friendly?*
                                    ''',
                                'Wrong_answers': ['They can befriend you if you feed them', 'No, they prefer solitude and live alone.'],
                                'Right_answer': 'Yes, very friendly',
                                'Theoretical_part': "By its nature, raccoons are extremely peaceful, friendly, active and inquisitive. If you don't believe me, ask Groot.",
                                'Video_url': 'https://dl.dropboxusercontent.com/u/20018982/K5KLPLf.mp4',
                                'Negative_answer': "Are you serious? Let's try again",
                                'Positive_answer': """
Exactly! Raccoons are champions of the world in  friendliness.
                                                   """,
                                'Order': 7,
                                'Next_step_order': 8})
        # Step 8
        self.mongo_client.send({'Problem': '''
While travelling to other zoos in search of carrots, Peter the Raccoon was rarely seen in the wild and mostly around the cafeterias and hot-dog stands.
*Can you believe that? Where do raccoons live nowadays?*
                                    ''',
                                'Wrong_answers': ['Wild nature with forests, rabbits, squirrels and other stuff'],
                                'Right_answer': 'Urban zones, cities, places with free wi-fi.',
                                'Theoretical_part': "Is native to North and South America having a range that extends from Southern Canada to the northern reaches of Argentina. Raccoons have feral populations in Europe, especially Germany, where they escaped from fur farms and were set loose to be hunted for sport during the time of World War II. Population densities of raccoons in urban areas can be 20 times higher than for raccoons in rural environments.",
                                'Negative_answer': "Really? Have you ever tried to live without free wi-fi for more than a week?",
                                'Positive_answer': "Thats right. There is no life without access to youtube.",
                                'Order': 8,
                                'Next_step_order': 9})
        # Step 9
        self.mongo_client.send({'Problem': '''
In several years of intense work, Peter the Raccoon was sighted in one of the southern zoos with great touristic infrastructure, not typical for “Mezhlissya”. Locals called him Procyon Lotor but animals in the zoo did not know what  this meant.
*What does raccoon’s scientific name Procyon Lotor mean?*
                                    ''',
                                'Wrong_answers': ['Water bear','Garage cat', 'Crazy mouse'],
                                'Right_answer': 'Washer dog',
                                'Image_url': 'http://cdn.ohmygodfacts.com/wp-content/uploads/2014/05/raccoon-04.jpg',
                                'Theoretical_part': "The raccoon’s scientific name, Procyon motor, means “washer dog” although it is a closer relative to the bear family.",
                                'Negative_answer': "All those names are awesome, but the truth is...",
                                'Positive_answer': "I bet you cheated on this question...",
                                'Order': 9,
                                'Next_step_order': 10})
        # Step 10
        self.mongo_client.send({'Problem': '''
All in all, the animals seem to be preparing for new elections and searching for new raccoons to lead them. Where can lots of smart racoons be found, how do you think?
*Where can you find raccoons in Ukraine today?*
                                            ''',
                                'Wrong_answers': [],
                                'Right_answer': 'More than 30 raccoons work in two hives (Kiev and Kharkiv offices). They will be really happy if you decide to join them tomorrow ;)',
                                'Positive_answer': """
Great job! I hope, you succeeded in completing the course, learn something new and laugh a lot. We will be in touch and update our course with new interesting facts about raccoon lives!
Go Raccoons!
                                """,
                                'Order': 10,
                                })