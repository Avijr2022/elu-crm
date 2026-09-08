import 'dart:convert';



import '../../../core/network/api_client.dart';



class CustomerContact {

  CustomerContact({

    required this.customerContactId,

    required this.firstName,

    this.lastName,

    this.email,

    this.phoneMobile,

    this.isPrimary = false,

  });



  final String customerContactId;

  final String firstName;

  final String? lastName;

  final String? email;

  final String? phoneMobile;

  final bool isPrimary;



  String get displayName =>

      [firstName, lastName].where((s) => s != null && s.isNotEmpty).join(' ');



  factory CustomerContact.fromJson(Map<String, dynamic> json) => CustomerContact(

        customerContactId: json['customer_contact_id'] as String,

        firstName: json['first_name'] as String,

        lastName: json['last_name'] as String?,

        email: json['email'] as String?,

        phoneMobile: json['phone_mobile'] as String?,

        isPrimary: json['is_primary'] as bool? ?? false,

      );

}



class CustomerAddress {

  CustomerAddress({

    required this.customerAddressId,

    required this.addressType,

    required this.addressLine1,

    this.city,

    this.state,

    this.country,

    this.postalCode,

  });



  final String customerAddressId;

  final String addressType;

  final String addressLine1;

  final String? city;

  final String? state;

  final String? country;

  final String? postalCode;



  String get summary {

    final parts = [addressLine1, city, state, postalCode, country]

        .where((p) => p != null && p.isNotEmpty)

        .join(', ');

    return parts;

  }



  factory CustomerAddress.fromJson(Map<String, dynamic> json) => CustomerAddress(

        customerAddressId: json['customer_address_id'] as String,

        addressType: json['address_type'] as String,

        addressLine1: json['address_line1'] as String,

        city: json['city'] as String?,

        state: json['state'] as String?,

        country: json['country'] as String?,

        postalCode: json['postal_code'] as String?,

      );

}



class Customer {

  Customer({

    required this.customerId,

    required this.customerNumber,

    required this.legalName,

    this.tradeName,

    required this.customerType,

    required this.status,

    this.sourceOpportunityId,

    this.notes,

    this.contacts = const [],

    this.addresses = const [],

    this.createdOn,

  });



  final String customerId;

  final String customerNumber;

  final String legalName;

  final String? tradeName;

  final String customerType;

  final String status;

  final String? sourceOpportunityId;

  final String? notes;

  final List<CustomerContact> contacts;

  final List<CustomerAddress> addresses;

  final DateTime? createdOn;



  factory Customer.fromJson(Map<String, dynamic> json) => Customer(

        customerId: json['customer_id'] as String,

        customerNumber: json['customer_number'] as String,

        legalName: json['legal_name'] as String,

        tradeName: json['trade_name'] as String?,

        customerType: json['customer_type'] as String,

        status: json['status'] as String,

        sourceOpportunityId: json['source_opportunity_id'] as String?,

        notes: json['notes'] as String?,

        contacts: (json['contacts'] as List<dynamic>? ?? [])

            .cast<Map<String, dynamic>>()

            .map(CustomerContact.fromJson)

            .toList(),

        addresses: (json['addresses'] as List<dynamic>? ?? [])

            .cast<Map<String, dynamic>>()

            .map(CustomerAddress.fromJson)

            .toList(),

        createdOn: json['created_on'] != null

            ? DateTime.tryParse(json['created_on'] as String)

            : null,

      );

}



class CustomerListResult {

  CustomerListResult({required this.items, required this.total});

  final List<Customer> items;

  final int total;



  factory CustomerListResult.fromJson(Map<String, dynamic> json) => CustomerListResult(

        items: (json['items'] as List<dynamic>? ?? [])

            .cast<Map<String, dynamic>>()

            .map(Customer.fromJson)

            .toList(),

        total: json['total'] as int? ?? 0,

      );

}



class CustomerService {

  CustomerService({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;



  Future<CustomerListResult> list({
    int page = 1,
    int pageSize = 25,
    String? search,
    String? status,
  }) async {
    final query = <String, String>{
      'page': '$page',
      'page_size': '$pageSize',
      if (search != null && search.isNotEmpty) 'search': search,
      if (status != null && status.isNotEmpty) 'status': status,
    };

    final res = await _client.get('/api/v1/crm/customers', query: query);

    if (res.statusCode != 200) {

      throw Exception(_client.extractError(res.body) ?? 'Failed to load customers');

    }

    return CustomerListResult.fromJson(jsonDecode(res.body) as Map<String, dynamic>);

  }



  Future<Customer> getById(String id) async {

    final res = await _client.get('/api/v1/crm/customers/$id');

    if (res.statusCode != 200) {

      throw Exception(_client.extractError(res.body) ?? 'Failed to load customer');

    }

    return Customer.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }

  Future<Customer> create({
    required String legalName,
    String? tradeName,
    String? notes,
  }) async {
    final res = await _client.post(
      '/api/v1/crm/customers',
      body: jsonEncode({
        'legal_name': legalName,
        if (tradeName != null) 'trade_name': tradeName,
        if (notes != null) 'notes': notes,
      }),
    );
    if (res.statusCode != 201) {
      throw Exception(_client.extractError(res.body) ?? 'Failed to create customer');
    }
    return Customer.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }

  Future<Customer> update(String id, {String? status}) async {
    final body = <String, dynamic>{};
    if (status != null) body['status'] = status;
    final res = await _client.patch('/api/v1/crm/customers/$id', body: body);
    if (res.statusCode != 200) {
      throw Exception(_client.extractError(res.body) ?? 'Failed to update customer');
    }
    return Customer.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }

  Future<CustomerContact> addContact(
    String customerId, {
    required String firstName,
    String? lastName,
    String? email,
    String? phoneMobile,
    bool isPrimary = false,
  }) async {
    final res = await _client.post(
      '/api/v1/crm/customers/$customerId/contacts',
      body: jsonEncode({
        'first_name': firstName,
        if (lastName != null) 'last_name': lastName,
        if (email != null) 'email': email,
        if (phoneMobile != null) 'phone_mobile': phoneMobile,
        'is_primary': isPrimary,
      }),
    );
    if (res.statusCode != 201) {
      throw Exception(_client.extractError(res.body) ?? 'Failed to add contact');
    }
    return CustomerContact.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }

  Future<CustomerAddress> addAddress(
    String customerId, {
    required String addressLine1,
    String addressType = 'REGISTERED',
    String? city,
    String? state,
    String? country,
    String? postalCode,
  }) async {
    final res = await _client.post(
      '/api/v1/crm/customers/$customerId/addresses',
      body: jsonEncode({
        'address_type': addressType,
        'address_line1': addressLine1,
        if (city != null) 'city': city,
        if (state != null) 'state': state,
        if (country != null) 'country': country,
        if (postalCode != null) 'postal_code': postalCode,
      }),
    );
    if (res.statusCode != 201) {
      throw Exception(_client.extractError(res.body) ?? 'Failed to add address');
    }
    return CustomerAddress.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }
}
