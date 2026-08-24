// ignore_for_file: unused_import, avoid_print, constant_identifier_names, duplicate_ignore

import 'package:customertracker/add_lead.dart';
import 'package:customertracker/lead_add_category_list.dart';
import 'package:customertracker/lead_profile.dart';
import 'package:customertracker/side_menu_app.dart';
import 'package:customertracker/user_add.dart';
import 'package:flutter/material.dart';

class LeadCategory extends StatelessWidget {
  const LeadCategory({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: LeadCategoryForm(),
    );
  }
}

class LeadCategoryForm extends StatefulWidget {
  const LeadCategoryForm({super.key});

  @override
  State<LeadCategoryForm> createState() => _LeadCategoryState();
}

class _LeadCategoryState extends State<LeadCategoryForm> {
  // This holds a list of fiction users
  // You can use data fetched from a database or a server as well
  final List<Map<String, dynamic>> _allUsers = [
    {"id": 1, "name": "All Leads", "count": "(6)"},
    {"id": 1, "name": "Call Logs", "count": "(0)"},
    {"id": 2, "name": "Existing Leads", "count": "(0)"},
    {"id": 3, "name": "Phone Contacts", "count": "(0)"},
    {"id": 3, "name": "Sample Leads", "count": "(6)"},
    {"id": 3, "name": "Website Enquires", "count": "(0)"},
  ];

  // This list holds the data for the list view
  List<Map<String, dynamic>> _foundUsers = [];
  @override
  initState() {
    // at the beginning, all users are shown
    _foundUsers = _allUsers;
    super.initState();
  }

  // This function is called whenever the text field changes

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      drawer: const NavDrawer(),
      appBar: AppBar(
        title: const Text(
          "Lead Category (6)",
          style: TextStyle(
              color: Color.fromARGB(255, 250, 249, 249), fontSize: 14),
        ),
        backgroundColor: const Color.fromARGB(100, 22, 44, 33),
        actions: <Widget>[
          Padding(
              padding: const EdgeInsets.only(right: 20.0),
              child: GestureDetector(
                onTap: () {},
                child: const Icon(
                  Icons.search,
                  color: Color.fromARGB(255, 252, 252, 252),
                  size: 25.0,
                ),
              )),
          Padding(
              padding: const EdgeInsets.only(right: 20.0),
              child: GestureDetector(
                onTap: () {},
                child: const Icon(
                  Icons.sort_by_alpha,
                  color: Color.fromARGB(255, 255, 255, 255),
                  size: 25.0,
                ),
              )),
          Padding(
              padding: const EdgeInsets.only(right: 20.0),
              child: GestureDetector(
                onTap: () {},
                child: const Icon(
                  Icons.info,
                  color: Color.fromARGB(255, 255, 255, 255),
                  size: 25.0,
                ),
              )),
        ],
      ),
      body: Container(
        padding: const EdgeInsets.only(left: 20.0, top: 0.0, right: 20.0),
        height: 1000,
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/images/cover.jpg'),
            fit: BoxFit.cover,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(2),
          child: Column(
            children: [
              Expanded(
                child: _foundUsers.isNotEmpty
                    ? ListView.builder(
                        itemCount: _foundUsers.length,
                        itemBuilder: (context, index) => Card(
                          key: ValueKey(_foundUsers[index]["id"]),
                          color: const Color.fromARGB(160, 244, 247, 98),
                          elevation: 7,
                          margin: const EdgeInsets.symmetric(vertical: 5),
                          child: ListTile(
                            leading: const CircleAvatar(
                              backgroundImage:
                                  AssetImage('assets/images/cover.jpg'),
                            ),
                            title: Text(_foundUsers[index]['name']),
                            subtitle:
                                Text(_foundUsers[index]["count"].toString()),
                            trailing: Wrap(
                              spacing: 12, // space between two icons
                              children: <Widget>[
                                PopupMenuButton<String>(
                                  onSelected: choiceAction,
                                  itemBuilder: (BuildContext context) {
                                    return Constants.choices
                                        .map((String choice) {
                                      return PopupMenuItem<String>(
                                        value: choice,
                                        child: Text(choice),
                                      );
                                    }).toList();
                                  },
                                )
                              ],
                            ),
                          ),
                        ),
                      )
                    : const Text(
                        'Sorry! No results found',
                        style: TextStyle(fontSize: 18),
                      ),
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.push(
              context,
              MaterialPageRoute(
                  builder: (context) => const AddLeadCategoryList()));
        },
        backgroundColor: const Color.fromARGB(255, 91, 92, 92),
        label: const Text('Lead Category'),
        icon: const Icon(Icons.person_add_alt_1_rounded),
      ),
    );
  }
}

class Constants {
  // ignore: constant_identifier_names
  static const String FirstItem = 'List Info';
  static const String SecondItem = 'Clone List';
  static const String ThiredItem = 'Edit List';
  static const String FourthItem = 'Delete List';

  static const List<String> choices = <String>[
    FirstItem,
    SecondItem,
    ThiredItem,
    FourthItem
  ];
}

void choiceAction(String choice) {
  if (choice == Constants.FirstItem) {
    print('I First Item');
  } else if (choice == Constants.SecondItem) {
    print('I Second Item');
  } else if (choice == Constants.ThiredItem) {
    print('I Thired Item');
  } else if (choice == Constants.FourthItem) {
    print('I Fourth Item');
  }
}
