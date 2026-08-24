// ignore_for_file: avoid_unnecessary_containers

import 'package:customertracker/user.dart';
import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:dropdown_button2/dropdown_button2.dart';

class AddUser extends StatelessWidget {
  const AddUser({super.key});

  @override
  Widget build(BuildContext context) {
    const appTitle = 'Add User';
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: appTitle,
      home: Scaffold(
        resizeToAvoidBottomInset: true,
        appBar: AppBar(
          backgroundColor: const Color.fromARGB(255, 91, 92, 92),
          actions: <Widget>[
            Padding(
                padding: const EdgeInsets.only(right: 20.0),
                child: GestureDetector(
                  onTap: () {
                    // Navigator.push(
                    //     context,
                    //     MaterialPageRoute(
                    //         builder: (context) => const UsersForm()));
                  },
                  child: const Icon(Icons.contact_phone_outlined),
                )),
            Padding(
                padding: const EdgeInsets.only(right: 20.0),
                child: GestureDetector(
                  onTap: () {
                    Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) => const UsersForm()));
                  },
                  child: const Icon(Icons.add_task),
                )),
          ],
          title: const Text(
            appTitle,
          ),
          leading: IconButton(
              onPressed: () {
                Navigator.pop(context);
              },
              icon: const Icon(
                Icons.arrow_back_ios,
                size: 20,
                color: Color.fromARGB(255, 252, 250, 250),
              )),
        ),
        body: Container(
          padding: const EdgeInsets.only(left: 20.0, top: 20.0, right: 20.0),
          height: 1000,
          decoration: const BoxDecoration(
            image: DecorationImage(
              image: AssetImage('assets/images/cover2.jpg'),
              fit: BoxFit.cover,
            ),
          ),
          child: const MyCustomForm(),
        ),
      ),
    );
  }
}

class MyCustomForm extends StatefulWidget {
  const MyCustomForm({super.key});

  @override
  MyCustomFormState createState() {
    return MyCustomFormState();
  }
}

class MyCustomFormState extends State<MyCustomForm> {
  final _formKey = GlobalKey<FormState>();
  TextEditingController passwordController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Container(
        child: SingleChildScrollView(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              Container(
                decoration: const BoxDecoration(
                  image: DecorationImage(
                    image: AssetImage('assets/images/cover.jpg'),
                    fit: BoxFit.cover,
                  ),
                  color: Color.fromARGB(100, 229, 238, 144),
                ),
                child: const CircleAvatar(
                  backgroundColor: Color.fromARGB(100, 229, 238, 144),
                  minRadius: 44.0,
                  child: Center(
                    child: CircleAvatar(
                      radius: 38.0,
                      backgroundColor: Color.fromARGB(100, 220, 228, 149),
                      backgroundImage: null,
                      child: ClipOval(
                        child: SizedBox(
                          width: 180.0,
                          height: 180.0,
                          child: Icon(Icons.camera_alt),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
              const Divider(
                color: Color.fromARGB(255, 91, 92, 92),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: TextFormField(
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.person),
                    hintText: 'Enter your First Name',
                    labelText: 'First Name',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    prefixIcon: Icon(Icons.person),
                    hintText: 'Enter your Last Name',
                    labelText: 'Last Name',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    prefixIcon: Icon(FontAwesomeIcons.userTie),
                    hintText: 'Enter your Designation',
                    labelText: 'Designation',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    prefixIcon: Icon(Icons.email),
                    hintText: 'Enter a email address',
                    labelText: 'Email',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    prefixIcon: Icon(Icons.phone),
                    hintText: 'Enter a phone number',
                    labelText: 'Phone',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                child: TextField(
                  obscureText: true,
                  controller: passwordController,
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.key),
                    suffixIcon: Icon(Icons.remove_red_eye),
                    hintText: 'Enter a passowrd',
                    labelText: 'Password',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                child: DropdownButtonHideUnderline(
                  child: DropdownButton2<String>(
                    isExpanded: true,
                    hint: Text(
                      'Select Role',
                      style: TextStyle(
                        fontSize: 20,
                        color: Theme.of(context).hintColor,
                      ),
                    ),
                    items: items
                        .map((item) => DropdownMenuItem(
                              value: item,
                              child: Text(
                                item,
                                style: const TextStyle(
                                  fontSize: 14,
                                ),
                              ),
                            ))
                        .toList(),
                    value: selectedValue,
                    onChanged: (value) {
                      setState(() {
                        selectedValue = value as String;
                      });
                    },
                    buttonStyleData: const ButtonStyleData(
                      height: 40,
                      width: 230,
                    ),
                    dropdownStyleData: const DropdownStyleData(
                      maxHeight: 200,
                    ),
                    menuItemStyleData: const MenuItemStyleData(
                      height: 40,
                    ),
                    dropdownSearchData: DropdownSearchData(
                      searchController: textEditingController,
                      searchInnerWidgetHeight: 40,
                      searchInnerWidget: Container(
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
                            contentPadding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 8,
                            ),
                            hintText: 'Search role...',
                            hintStyle: const TextStyle(fontSize: 16),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                        ),
                      ),
                      searchMatchFn: (item, searchValue) {
                        return (item.value.toString().contains(searchValue));
                      },
                    ),
                    //This to clear the search value when you close the menu
                    onMenuStateChange: (isOpen) {
                      if (!isOpen) {
                        textEditingController.clear();
                      }
                    },
                  ),
                ),
              ),
              const Divider(
                color: Color.fromARGB(255, 91, 92, 92),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

final List<String> items = [
  'Select Role',
  'Account Owner',
  'Manager',
  'L1 User',
  'L2 User',
];

String? selectedValue;
final TextEditingController textEditingController = TextEditingController();
