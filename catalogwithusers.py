from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Category, Base, Item, User
 
engine = create_engine('sqlite:///catalogwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

user1 = User(username='Simi Agarwal', email='1simiagarwal@gmail.com')
session.add(user1)
session.commit()

#basketball items 
category1 = Category(name = "Basketball", user = user1)

session.add(category1)
session.commit()




Item1 = Item(
	name = "Ball1",
	description = "UNDER ARMOUR 495 INDOOR/OUTDOOR BALL - MEN'S",
	price = "$40.00",
	category_id= category1.id,
	category_name = category1.name,
	user = user1


)

session.add(Item1)
session.commit()

Item2 = Item(
	name = "ball2",
	description = "NIKE VERSA TACK BASKETBALL - MEN'S", 
	price = "$89.99",
	category_id = category1.id,
	category_name = category1.name,
	user= user1
	)
	

session.add(Item2)
session.commit()

Item3 = Item(
	name ="bag1",
	description = "NIKE HOOPS ELITE MAX AIR 2.0 BACKPACK", 
	price = "$183.99",
	category_id= category1.id,
	category_name = category1.name,
	user= user1
	
	)

session.add(Item3)
session.commit()

Item4 = Item(
	name="bag2",
	description = "JORDAN RETRO 13 BACKPACK",
	price = "$150.00",
	category_id = category1.id,
	category_name = category1.name,
	user = user1
	
	)

session.add(Item4)
session.commit()

Item5 = Item(
	name ="shoes1",
	description = "Unique cushioning features for all-day wear.", 
	price = "$61.99",
	category_id = category1.id,
	category_name = category1.name,
	user= user1
	
	)

session.add(Item5)
session.commit()

Item6 = Item(
	name = "shoes2",
	description = "NIKE KOBE A.D. - MEN'S", 
 	price = "$96.99",
 	category_id = category1.id,
 	category_name = category1.name,
 	user = user1
 	
 	)

session.add(Item6)
session.commit()

Item7 = Item(
    name ="shirt1",
	description = "comfortable cotton shirt", 
	price = "$29.00",
	category_id = category1.id,
	category_name = category1.name,
	user = user1
	
	)

session.add(Item7)
session.commit()






# soccer Items
category2 = Category( name ='soccer', user = user1)

session.add(category2)
session.commit()


Item1 = Item(
	name = "ball1",
	description = "NIKE STRIKE SOCCER BALL.", 
	price = "$47.99",
	category_id = category2.id,
	category_name = category2.name,
	user= user1
	
	)

session.add(Item1)
session.commit()

Item2 = Item(
	name ="shirt1",
	description = " delivers a soft feel, sweat-wicking performance",
	price = "$25",
	category_id = category2.id,
	category_name = category2.name,
	user= user1
	
	)

session.add(Item2)
session.commit()

Item3 = Item(
	name="pants1",
	description = "Cotton",
	price = "$59.99",
	category_id = category2.id,
	category_name = category2.name,
	user= user1
	)

session.add(Item3)
session.commit()

Item4 = Item(
	name="pants2",
	description = "Mixed", 
	price = "$40.00",
	category_id = category2.id,
	category_name = category2.name,
	user = user1
	
	)

session.add(Item4)
session.commit()

Item5 = Item(
	name = "shoes1",
	description = "ADIDAS NEMEZIZ TANGO 17.1 TRAINER - MEN'S", 
	price = "$150.00",
	category_id = category2.id,
	category_name = category2.name,
	user= user1
	
	)

session.add(Item5)
session.commit()

Item6 = Item(
	name ="shoes2",
	description = "ADIDAS NEMEZIZ TANGO 17.1 TRAINER - MEN'S",
	price = "$99.00",
	category_id = category2.id,
	category_name = category2.name,
	user= user1
	
	)

session.add(Item6)
session.commit()




# baseball items
category3 = Category(name = "baseball",user=user1)

session.add(category3)
session.commit()


Item1 = Item(
	name = "Bat1",
	description = "Louisville Slugger Junior Big Barrel Omaha 517 2 3/4 (-10) Baseball Bat", 
	price = "$69.99",
	category_id = category3.id,
	category_name = category3.name,
	user= user1
	
	
	)

session.add(Item1)
session.commit()

Item2 = Item(
	name = "Bat2",
	description = "FLASHTEK Natural Baseball Bat",
	price = "18.99",
	category_id = category3.id,
	category_name = category3.name,
	user= user1
	
	)

session.add(Item2)
session.commit()

Item3 = Item(
	name="shoes1",
	description = "Under Armour Men's Leadoff Low RM Baseball Cleats", 
	price = "$89.99", 
	category_id = category3.id,
	category_name = category3.name,
	user= user1
	

	)

session.add(Item3)
session.commit()

Item4 = Item(
	name = "bag1",
	description = "Athletico Baseball Bat Bag - Backpack for Baseball, T-Ball & Softball Equipment & Gear for Kids, Youth, and Adults | Holds Bat, Helmet, Glove, & Shoes | Separate Shoe Compartment, & Fence Hook",
	price = "$59.99",
	category_id = category3.id,
	category_name = category3.name,
	user = user1
	
	)

session.add(Item4)
session.commit()
###########
user3 = User(username='Bob', email='bob@yahoo.com')
session.add(user3)
session.commit()

#Cricket
category5 = Category(name = "Cricket", user = user3)

session.add(category5)
session.commit()




Item1 = Item(
	name = "Bat",
	description = "Revolution 101 ",
	price = "$100.00",
	category_id= category5.id,
	category_name = category5.name,
	user = user3
	
	
)

session.add(Item1)
session.commit()

Item2 = Item(
	name = "Bat2",
	description = "BAS DOLPHIN PROFILE PLAIN BAT (VK)", 
	price = "$49.99",
	category_id= category5.id,
	category_name = category5.name,
	user = user3
	)
	

session.add(Item2)
session.commit()

Item3 = Item(
	name ="Batting gloves",
	description = "Dry Bag Waterproof Floating Dry Gear Bags for Boating, Kayaking, Fishing, Rafting, Swimming, Camping and Snowboarding-Camouflage ", 
	price = "$24.99",
	category_id= category5.id, 
	category_name = category5.name,
	user = user3
	
	)

session.add(Item3)
session.commit()

Item4 = Item(
	name="Batting gloves 2",
	description = "GM 808 LE CRICKET BATTING GLOVES 2017",
	price="$99.00",
	category_id= category5.id,
	category_name = category5.name,
	user = user3
	
	)

session.add(Item4)
session.commit()

Item5 = Item(
	name ="GRAY NICOLLS BALLS",
	description = "GN League Pink Cricket Ball", 
	price = "$61.99",
	category_id= category5.id,
	category_name = category5.name,
	user = user3
	
	)

session.add(Item5)
session.commit()

Item6 = Item(
	name = "shoes2",
	description = "ADIDAS ADIZERO BOOST SL22 CRICKET SHOES 2017", 
 	price = "$115.99",
	category_id = category5.id,
 	category_name = category5.name,
 	user = user3
 	
 	)

session.add(Item6)
session.commit()

Item7 = Item(
    name ="shoes1",
	description = "ADIDAS ADIPOWER VECTOR CRICKET SHOES",
	price = "$130.99",
	category_id= category5.id,
	category_name = category5.name,
	user= user3
	
	)

session.add(Item7)
session.commit()

Item8 = Item(
	name = "Bat cover",
	description = "GM CRICKET FULL LENGTH BAT COVER",
 	price="$59.99",
 	category_id= category5.id,
 	category_name = category5.name,
 	user = user3
 	
 	)

session.add(Item8)
session.commit()

