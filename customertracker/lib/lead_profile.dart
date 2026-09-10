// ignore_for_file: sized_box_for_whitespace, constant_identifier_names, duplicate_ignore, avoid_print, unnecessary_const

import 'package:customertracker/lead_profile_add_followup.dart';
import 'package:customertracker/lead_profile_attchments.dart';
import 'package:customertracker/lead_profile_qualifiers.dart';
import 'package:customertracker/lead_profile_quotesinvoices.dart';
import 'package:customertracker/lead_profile_recent_activity.dart';
import 'package:flutter/material.dart';

import 'lead_edit_profile.dart';

class LeadProfile extends StatelessWidget {
  const LeadProfile({super.key});

  // This widget is the root of the application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Profile',
      debugShowCheckedModeBanner: false,
      home: Scaffold(
          appBar: AppBar(
            leading: Padding(
                padding: const EdgeInsets.only(right: 20.0),
                child: GestureDetector(
                  onTap: () {
                    Navigator.pop(context);
                  },
                  child: const Icon(Icons.arrow_back_ios_new),
                )),
            actions: <Widget>[
              Padding(
                  padding: const EdgeInsets.only(right: 20.0),
                  child: GestureDetector(
                    onTap: () {
                      Navigator.push(
                          context,
                          MaterialPageRoute(
                              builder: (context) => const LeadEditprofile()));
                    },
                    child: const Icon(Icons.add_card_rounded),
                  )),
              Padding(
                  padding: const EdgeInsets.only(right: 20.0),
                  child: GestureDetector(
                    onTap: () {
                      Navigator.push(
                          context,
                          MaterialPageRoute(
                              builder: (context) => const LeadEditprofile()));
                    },
                    child: const Icon(Icons.edit),
                  )),
              PopupMenuButton<String>(
                onSelected: choiceAction,
                itemBuilder: (BuildContext context) {
                  return Constants.choices.map((String choice) {
                    return PopupMenuItem<String>(
                      value: choice,
                      child: Text(choice),
                    );
                  }).toList();
                },
              )
            ],
            backgroundColor: const Color.fromARGB(255, 91, 92, 92),
            title: const Text('Profile'),
          ),
          body: Container(
            padding: const EdgeInsets.only(left: 20.0, top: 20.0, right: 20.0),
            height: 1000,
            decoration: const BoxDecoration(
              image: DecorationImage(
                image: AssetImage('assets/images/cover.jpg'),
                fit: BoxFit.cover,
              ),
            ),
            child: ListView(
              children: <Widget>[
                Container(
                  width: 150,
                  child: const Column(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    mainAxisAlignment: MainAxisAlignment.center,
                    // ignore: prefer_const_literals_to_create_immutables
                    children: <Widget>[
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: <Widget>[
                          CircleAvatar(
                            backgroundColor: Color.fromARGB(179, 255, 255, 255),
                            minRadius: 45.0,
                            child: CircleAvatar(
                                radius: 40.0,
                                backgroundImage:
                                    AssetImage('assets/images/cover2.jpg')),
                          ),
                        ],
                      ),
                      SizedBox(
                        height: 10,
                      ),
                      Text(
                        'XXXXXXX XXXXXXXXX',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Color.fromARGB(255, 56, 55, 55),
                        ),
                      ),
                      Text(
                        'Project Manager',
                        style: TextStyle(
                          color: Color.fromARGB(255, 56, 55, 55),
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        'xxxxxxxxxxxx',
                        style: TextStyle(
                          color: Color.fromARGB(255, 56, 55, 55),
                          fontSize: 15,
                        ),
                      ),
                      Text(
                        'ytryfjhjgkjhkh',
                        style: TextStyle(
                          color: Color.fromARGB(255, 56, 55, 55),
                          fontSize: 12,
                        ),
                      ),
                      Text(
                        'jgjhfdgfd',
                        style: TextStyle(
                          color: Color.fromARGB(255, 56, 55, 55),
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(
                  height: 10,
                ),
                Row(
                  // scrollDirection: Axis.horizontal,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: <Widget>[
                    SizedBox(
                      width: 26,
                      height: 25,
                      child: FittedBox(
                        child: FloatingActionButton.small(
                          //<-- SEE HERE
                          backgroundColor: Colors.red,
                          onPressed: () {},
                          child: const Icon(
                            Icons.call,
                            size: 30,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(
                      width: 12,
                    ),
                    SizedBox(
                      width: 26,
                      height: 25,
                      child: FittedBox(
                        child: FloatingActionButton.small(
                          backgroundColor: Colors.green,
                          onPressed: () {},
                          child: const Icon(
                            Icons.apartment,
                            size: 30,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(
                      width: 12,
                    ),
                    SizedBox(
                      width: 26,
                      height: 25,
                      child: FittedBox(
                        child: FloatingActionButton.small(
                          backgroundColor: Colors.blue[600],
                          onPressed: () {},
                          child: const Icon(
                            Icons.chat,
                            size: 30,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(
                      width: 12,
                    ),
                    SizedBox(
                      width: 26,
                      height: 25,
                      child: FittedBox(
                        child: FloatingActionButton.small(
                          backgroundColor: Colors.red[400],
                          onPressed: () {},
                          child: const Icon(
                            Icons.mail,
                            size: 30,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(
                      width: 12,
                    ),
                    SizedBox(
                      width: 26,
                      height: 25,
                      child: FittedBox(
                        child: FloatingActionButton.small(
                          backgroundColor: Colors.pink[300],
                          onPressed: () {},
                          child: const Icon(
                            Icons.attachment,
                            size: 30,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(
                      width: 12,
                    ),
                    SizedBox(
                      width: 26,
                      height: 25,
                      child: FittedBox(
                        child: FloatingActionButton.small(
                          backgroundColor: Colors.yellow[900],
                          onPressed: () {},
                          child: const Icon(
                            Icons.location_pin,
                            size: 30,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(
                      width: 12,
                    ),
                    SizedBox(
                      width: 26,
                      height: 25,
                      child: FittedBox(
                        child: FloatingActionButton.small(
                          backgroundColor: Colors.teal[900],
                          onPressed: () {},
                          child: const Icon(
                            Icons.currency_rupee_rounded,
                            size: 30,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(
                      width: 12,
                    ),
                    SizedBox(
                      width: 26,
                      height: 25,
                      child: FittedBox(
                        child: FloatingActionButton.small(
                          backgroundColor: Colors.red[700],
                          onPressed: () {},
                          child: const Icon(
                            Icons.share,
                            size: 30,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(
                      width: 12,
                    ),
                    SizedBox(
                      width: 26,
                      height: 25,
                      child: FittedBox(
                        child: FloatingActionButton.small(
                          backgroundColor: Colors.grey[700],
                          onPressed: () {},
                          child: const Icon(
                            Icons.calendar_month_outlined,
                            size: 30,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(
                      width: 10,
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                const Divider(
                  color: Color.fromARGB(255, 91, 92, 92),
                ),
                const SizedBox(height: 20),
                Column(
                  children: <Widget>[
                    InkWell(
                      onTap: () {
                        Navigator.push(
                            context,
                            MaterialPageRoute(
                                builder: (context) =>
                                    const PeofileFollowupLayout()));
                      },
                      child: const Card(
                        elevation: 50,
                        shadowColor: Colors.black,
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: <Widget>[
                            ListTile(
                              leading: Icon(Icons.add_circle,
                                  size: 50, color: Colors.green),
                              title: Text(
                                  'Assignment & Follow-up\nAssigned to xxxxxxx'),
                              subtitle: Text('Set follow-up'),
                            ),
                          ],
                        ),
                      ),
                    ),
                    InkWell(
                      onTap: () {
                        Navigator.push(
                            context,
                            MaterialPageRoute(
                                builder: (context) =>
                                    const Leadrecentactivity()));
                      },
                      child: const Card(
                        elevation: 50,
                        shadowColor: Colors.black,
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: <Widget>[
                            ListTile(
                              leading: Icon(Icons.run_circle_sharp,
                                  size: 50,
                                  color: Color.fromARGB(255, 248, 212, 4)),
                              title: Text('Recent Activity'),
                              subtitle: Text(''),
                            ),
                          ],
                        ),
                      ),
                    ),
                    InkWell(
                      onTap: () {
                        Navigator.push(
                            context,
                            MaterialPageRoute(
                                builder: (context) =>
                                    const LeadProfileQuotesInvoices()));
                      },
                      child: const Card(
                        elevation: 50,
                        shadowColor: Colors.black,
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: <Widget>[
                            ListTile(
                              leading: Icon(Icons.request_quote_outlined,
                                  size: 50,
                                  color: Color.fromARGB(255, 4, 49, 250)),
                              title: Text('Quotes & Invoices'),
                              subtitle: Text(''),
                            ),
                          ],
                        ),
                      ),
                    ),
                    InkWell(
                      onTap: () {
                        Navigator.push(
                            context,
                            MaterialPageRoute(
                                builder: (context) =>
                                    const LeadProfileQualifiersLayout()));
                      },
                      child: const Card(
                        elevation: 50,
                        shadowColor: Colors.black,
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: <Widget>[
                            ListTile(
                              leading: Icon(Icons.traffic_outlined,
                                  size: 35,
                                  color: Color.fromARGB(255, 78, 31, 105)),
                              title: Text('Qualifiers'),
                              subtitle: Text(''),
                            ),
                          ],
                        ),
                      ),
                    ),
                    InkWell(
                      onTap: () {
                        Navigator.push(
                            context,
                            MaterialPageRoute(
                                builder: (context) => const LeadAttachments()));
                      },
                      child: const Card(
                        elevation: 50,
                        shadowColor: Colors.black,
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: <Widget>[
                            ListTile(
                              leading: Icon(Icons.attach_file_outlined,
                                  size: 35,
                                  color: Color.fromARGB(255, 19, 51, 20)),
                              title: Text('Attachments'),
                              subtitle: Text(''),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          )),
    );
  }
}

class Constants {
  // ignore: constant_identifier_names
  static const String FirstItem = 'Clone Lead';
  static const String SecondItem = 'Delete Lead';
  static const String ThirdItem = 'Save to contact';

  static const List<String> choices = <String>[
    FirstItem,
    SecondItem,
    ThirdItem,
  ];
}

void choiceAction(String choice) {
  if (choice == Constants.FirstItem) {
    print('I First Item');
  } else if (choice == Constants.SecondItem) {
    print('I Second Item');
  } else if (choice == Constants.ThirdItem) {
    print('I Third Item');
  }
}
