// import 'package:customertracker/add_lead.dart';
// ignore_for_file: unused_import

import 'package:customertracker/lead_category.dart';
import 'package:customertracker/lead_contact_norms.dart';
import 'package:customertracker/lead_profile.dart';
import 'package:flutter/material.dart';

class LeadContacts extends StatelessWidget {
  const LeadContacts({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: AllLeadsPage(),
    );
  }
}

class AllLeadsPage extends StatefulWidget {
  const AllLeadsPage({super.key});

  @override
  State<AllLeadsPage> createState() => _AllLeadsPageState();
}

class _AllLeadsPageState extends State<AllLeadsPage> {
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "All leads",
          style: TextStyle(color: Color.fromARGB(255, 250, 249, 249)),
        ),
        leading: const Icon(
          Icons.list,
          color: Color.fromARGB(255, 249, 250, 250),
        ),
        // title: const Text(title),

        backgroundColor: const Color.fromARGB(100, 22, 44, 33),
        actions: <Widget>[
          Padding(
              padding: const EdgeInsets.only(right: 20.0),
              child: GestureDetector(
                onTap: () {
                  Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) => const LeadCategory()));
                },
                child: const Icon(
                  Icons.groups_outlined, //LeadCategory
                  color: Color.fromARGB(255, 252, 252, 252),
                  size: 25.0,
                ),
              )),
          Padding(
              padding: const EdgeInsets.only(right: 20.0),
              child: GestureDetector(
                onTap: () {
                  Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) => const LeadCategory()));
                }, // LeadCategory
                child: const Icon(
                  Icons.filter_list,
                  color: Color.fromARGB(255, 255, 255, 255),
                  size: 25.0,
                ),
              )),
        ],
      ),
      body: Container(
        padding: const EdgeInsets.only(left: 10.0, top: 0.0, right: 10.0),
        height: 1000,
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/images/cover.jpg'),
            fit: BoxFit.cover,
          ),
        ),
        child: InkWell(
          onTap: () {
            Navigator.push(context,
                MaterialPageRoute(builder: (context) => const LeadProfile()));
          },
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
                              subtitle: Text(
                                  _foundUsers[index]["phoneno"].toString()),
                              trailing: const Wrap(
                                spacing: 12, // space between two icons
                                // children: [
                                //   IconButton(
                                //     onPressed: () {
                                //       Navigator.push(
                                //           context,
                                //           MaterialPageRoute(
                                //               builder: (context) =>
                                //                   const LeadProfile()));
                                //     },
                                //     icon: const Icon(Icons.arrow_circle_right),
                                //   ),
                                // ],
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
      ),
    );
  }
}
