// ignore_for_file: use_super_parameters

import 'package:customertracker/lead_profile.dart';
import 'package:customertracker/lead_state.dart';
import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

class LeadSearch extends StatelessWidget {
  const LeadSearch({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: SearchPage(),
    );
  }
}

class SearchPage extends StatefulWidget {
  const SearchPage({Key? key}) : super(key: key);

  @override
  State<SearchPage> createState() => _SearchPageState();
}

class _SearchPageState extends State<SearchPage> {
  // This holds a list of fiction users
  // You can use data fetched from a database or a server as well
  final List<Map<String, dynamic>> _allUsers = [
    {"id": 1, "name": "Amalendu Chatterjee", "phoneno": "+91 9836177764"},
    {"id": 2, "name": "Avijit Roy", "phoneno": "+91 9831098013"},
    {"id": 3, "name": "Biswajit Jana", "phoneno": "+91 8768201529"},
    {"id": 4, "name": "Bidhan Maity", "phoneno": "+91 8670114294"},
    {"id": 5, "name": "Shamba Bhanja", "phoneno": "+91 9007569640"},
    {"id": 6, "name": "Akram Ali", "phoneno": "+91 7003715942"},
    {"id": 7, "name": "Shankha Bhanja", "phoneno": "+91 9804199360"},
    {"id": 8, "name": "Ranadeep Dhar", "phoneno": "+91 7278788483"},
    {"id": 9, "name": "Priyabrata Seal", "phoneno": "+91 9836177769"},
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
  void _runFilter(String enteredKeyword) {
    List<Map<String, dynamic>> results = [];
    if (enteredKeyword.isEmpty) {
      // if the search field is empty or only contains white-space, we'll display all users
      results = _allUsers;
    } else {
      results = _allUsers
          .where((user) =>
              user["name"].toLowerCase().contains(enteredKeyword.toLowerCase()))
          .toList();
      // we use the toLowerCase() method to make it case-insensitive
    }

    // Refresh the UI
    setState(() {
      _foundUsers = results;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: TextField(
          // maxLines: 1,
          style: const TextStyle(
            fontSize: 17,
            color: Color.fromARGB(255, 250, 247, 248),
          ),
          textAlignVertical: TextAlignVertical.center,
          cursorColor: const Color.fromARGB(255, 168, 160, 163),

          decoration: const InputDecoration(
            border: InputBorder.none,
            focusedBorder: InputBorder.none,
            enabledBorder: InputBorder.none,
            errorBorder: InputBorder.none,
            disabledBorder: InputBorder.none,
            hintText: 'Search...',
            hintStyle: TextStyle(color: Color.fromARGB(255, 168, 160, 163)),
            // labelStyle: TextStyle(color: Color.fromARGB(255, 248, 248, 248)),
          ),
          onChanged: (value) => _runFilter(value),
        ),

        // const Text('Search Leads'),
        backgroundColor: const Color.fromARGB(255, 91, 92, 92),
        leading: IconButton(
            onPressed: () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (context) => const Leadstate()));
            },
            icon: const Icon(
              Icons.arrow_back_ios,
              size: 15,
              color: Color.fromARGB(255, 248, 247, 247),
            )),
        actions: [
          IconButton(
              onPressed: () {
                Navigator.push(context,
                    MaterialPageRoute(builder: (context) => const Leadstate()));
              },
              icon: const Icon(
                FontAwesomeIcons.sliders,
                size: 15,
                color: Color.fromARGB(255, 248, 247, 247),
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
                              children: [
                                IconButton(
                                  onPressed: () {
                                    Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                            builder: (context) =>
                                                const LeadProfile()));
                                  },
                                  icon: const Icon(Icons.arrow_circle_right),
                                ),
                                // Icon(Icons.arrow_circle_right), // icon-1
                                // Icon(Icons.message), // icon-2
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
    );
  }
}
