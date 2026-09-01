// ignore_for_file: unnecessary_const, avoid_unnecessary_containers, unused_import, unnecessary_null_comparison, avoid_print

import 'package:customertracker/lead_add_followup.dart';
import 'package:customertracker/lead_add_qualifiers.dart';
import 'package:customertracker/lead_select_list.dart';
import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:dropdown_button2/dropdown_button2.dart';

class Addleadbarstate extends StatefulWidget {
  const Addleadbarstate({super.key});

  @override
  State<Addleadbarstate> createState() => _AddleadbarstateState();
}

class _AddleadbarstateState extends State<Addleadbarstate> {
  final List<String> items = ['Item 1', 'Item 2', 'Item 3', 'Item 4'];
  String? selectedValue;
  final TextEditingController textEditingController = TextEditingController();

  // Explicitly declared value listener for compliance with version 3+ structure
  late final ValueNotifier<String?> selectedValueNotifier;

  @override
  void initState() {
    super.initState();
    selectedValueNotifier = ValueNotifier<String?>(selectedValue);
    selectedValueNotifier.addListener(() {
      setState(() {
        selectedValue = selectedValueNotifier.value;
      });
    });
  }

  @override
  void dispose() {
    textEditingController.dispose();
    selectedValueNotifier.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: DefaultTabController(
        length: 3,
        child: Scaffold(
          appBar: AppBar(
            backgroundColor: const Color.fromARGB(255, 91, 92, 92),
            leading: IconButton(
                onPressed: () {
                  Navigator.pop(context);
                },
                icon: const Icon(
                  Icons.arrow_back_ios,
                  size: 15,
                  color: Color.fromARGB(255, 248, 247, 247),
                )),
            bottom: const TabBar(
              tabs: [
                Tab(text: "PROFILE"),
                Tab(text: "QUALIFIERS"),
                Tab(text: "FOLLOW-UP"),
              ],
            ),
            actions: <Widget>[
              Padding(
                  padding: const EdgeInsets.only(
                      right: 20.0, left: 20.0, top: 20.0, bottom: 20.0),
                  child: GestureDetector(
                    onTap: () {},
                    child: const Text('Save'),
                  )),
            ],
            title: const Text('Add Lead'),
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
            child: TabBarView(
              children: <Widget>[
                Center(
                  child: SingleChildScrollView(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: <Widget>[
                        Container(
                          child: const CircleAvatar(
                            backgroundColor: Color.fromARGB(88, 255, 255, 255),
                            minRadius: 44.0,
                            child: Center(
                              child: CircleAvatar(
                                backgroundColor:
                                    Color.fromARGB(255, 148, 151, 151),
                                radius: 40.0,
                                backgroundImage: null,
                                child: ClipOval(
                                  child: SizedBox(
                                    width: 180.0,
                                    height: 180.0,
                                    child: Icon(Icons.camera),
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                        const Divider(
                          color: Color.fromARGB(255, 42, 90, 250),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          // Sizedbox controls overall drop-down button layout size safely
                          child: SizedBox(
                            width: 230,
                            child: DropdownButtonHideUnderline(
                              child: DropdownButtonFormField2<String>(
                                isExpanded: true,
                                hint: Text(
                                  'Select List',
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Theme.of(context).hintColor,
                                  ),
                                ),
                                items: items
                                    .map((item) => DropdownItem<String>(
                                          value: item,
                                          // Set individual dropdown height parameter explicitly here
                                          height: 40,
                                          child: Text(item,
                                              style: const TextStyle(
                                                  fontSize: 14)),
                                        ))
                                    .toList(),
                                valueListenable: selectedValueNotifier,
                                dropdownStyleData: const DropdownStyleData(
                                  maxHeight: 200,
                                ),
                                menuItemStyleData: const MenuItemStyleData(),
                                dropdownSearchData: DropdownSearchData(
                                  searchController: textEditingController,
                                  // Fixed parameter name changes from v3.0 Breaking Changes update
                                  searchBarWidgetHeight: 40,
                                  searchBarWidget: Container(
                                    height: 40,
                                    padding: const EdgeInsets.only(
                                      top: 8,
                                      bottom: 4,
                                      right: 8,
                                      left: 8,
                                    ),
                                    child: TextFormField(
                                      expands: true,
                                      maxLines: null,
                                      controller: textEditingController,
                                      decoration: InputDecoration(
                                        icon: const Icon(Icons.gpp_good),
                                        isDense: true,
                                        contentPadding:
                                            const EdgeInsets.symmetric(
                                          horizontal: 10,
                                          vertical: 8,
                                        ),
                                        hintText: 'Search List',
                                        hintStyle:
                                            const TextStyle(fontSize: 16),
                                        border: OutlineInputBorder(
                                          borderRadius:
                                              BorderRadius.circular(8),
                                        ),
                                      ),
                                    ),
                                  ),
                                  searchMatchFn: (item, searchValue) {
                                    return (item.value
                                        .toString()
                                        .toLowerCase()
                                        .contains(searchValue.toLowerCase()));
                                  },
                                ),
                                onMenuStateChange: (isOpen) {
                                  if (!isOpen) {
                                    textEditingController.clear();
                                  }
                                },
                              ),
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(),
                        ),
                      ],
                    ),
                  ),
                ),
                const Center(child: Text("Qualifiers Content")),
                const Center(child: Text("Follow-up Content")),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
