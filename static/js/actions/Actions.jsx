import { SET_DATA, SET_STAGE, SET_FILE, 
    ADD_CHARITY_NUMBERS, ADD_ORG_RECORD, SET_FIELD_NAMES, SET_FIELDS_TO_ADD } from "../constants/action-types";

export const set_data = (data, fields) => ({ type: SET_DATA, payload: {data: data, fields: fields}});
export const set_stage = stage => ({ type: SET_STAGE, payload: stage});
export const set_file = file => ({ type: SET_FILE, payload: file});
export const add_charity_numbers = charity_numbers => ({ type: ADD_CHARITY_NUMBERS, payload: charity_numbers});
export const add_org_record = (charity_number, record) => ({ type: ADD_ORG_RECORD, payload: { charity_number: charity_number, record: record } });
export const set_fields_to_add = fields_to_add => ({ type: SET_FIELDS_TO_ADD, payload: fields_to_add });
export const set_field_names = (field_name, field_value) => ({ 
    type: SET_FIELD_NAMES, 
    payload: { 
        field_name: field_name, 
        field_value: field_value
    } 
});
