// ignore_for_file: unused_import, avoid_print, constant_identifier_names, duplicate_ignore

import 'package:customertracker/add_lead.dart';
import 'package:customertracker/lead_profile.dart';
import 'package:customertracker/side_menu_app.dart';
import 'package:customertracker/user_add.dart';
import 'package:flutter/material.dart';

class UsersForm extends StatelessWidget {
  const UsersForm({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: AllUsersForm(),
    );
  }
}

class AllUsersForm extends StatefulWidget {
  const AllUsersForm({super.key});

  @override
  State<AllUsersForm> createState() => _AllUsersFormState();
}

class _AllUsersFormState extends State<AllUsersForm> {
  // This holds a list of fiction users
  // You can use data fetched from a database or a server as well
  final List<Map<String, dynamic>> _allUsers = [
    {"id": 1, "name": "Tarak Basak", "phoneno": "+91 9674900101"},
    {"id": 2, "name": "Subha Bhattacharjee", "phoneno": "+91 9748630363"},
    {"id": 3, "name": "Avik Dey", "phoneno": "+91 62900 64896"},
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
          "Users",
          style: TextStyle(color: Color.fromARGB(255, 250, 249, 249)),
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
                  Icons.info,
                  color: Color.fromARGB(255, 255, 255, 255),
                  size: 25.0,
                ),
              )),
          Padding(
              padding: const EdgeInsets.only(right: 20.0),
              child: GestureDetector(
                onTap: () {},
                child: const Icon(
                  Icons.settings_accessibility_sharp,
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
                                Text(_foundUsers[index]["phoneno"].toString()),
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
          Navigator.push(context,
              MaterialPageRoute(builder: (context) => const AddUser()));
        },
        backgroundColor: const Color.fromARGB(255, 91, 92, 92),
        label: const Text('ADD USER'),
        icon: const Icon(Icons.person_add_alt_1_rounded),
      ),
    );
  }
}

class Constants {
  // ignore: constant_identifier_names
  static const String FirstItem = 'Edit User';
  static const String SecondItem = 'View Performance';

  static const List<String> choices = <String>[
    FirstItem,
    SecondItem,
  ];
}

void choiceAction(String choice) {
  if (choice == Constants.FirstItem) {
    print('I First Item');
  } else if (choice == Constants.SecondItem) {
    print('I Second Item');
  }
}
