import { MATCH_RESULT, UNMATCH_RESULT, TOGGLE_FIELD, SET_DATA, SET_STAGE, SET_FILE, 
    ADD_CHARITY_NUMBERS, ADD_ORG_RECORD, SET_FIELD_NAMES, SET_FIELDS_TO_ADD } from "../constants/action-types";

const initialState = {
    stage: 'upload',
    data: [],
    reconcile_field: "charity_name",
    charity_number_field: "charity_number",
    org_id_field: "",
    fields: [],
    reconcile_results: {},
    hidden_fields: [],
    file: null,
    charity_numbers: null,
    fields_to_add: ['postcode'],
    org_data: {},
    progress: 0,
    loading: false,
};

const amendRow = (data, rowid, row) => {
    return [
        ...data.slice(0, rowid),
        row,
        ...data.slice(rowid + 1)
    ];
};

const rootReducer = (state = initialState, action) => {
    switch (action.type) {
        case MATCH_RESULT:
            var row = {...state.data[action.payload.rowid],
                [state.charity_number_field]: action.payload.result.id
            };
            return { ...state, data: amendRow(state.data, action.payload.rowid, row) };
        case UNMATCH_RESULT:
            var row = Object.assign({}, state.data[action.payload], {
                [state.charity_number_field]: null
            });
            return { ...state, data: amendRow(state.data, action.payload, row) };
        case TOGGLE_FIELD:
            var field_index = state.hidden_fields.indexOf(action.payload);
            if (field_index) {
                return { ...state, hidden_fields: [...state.hidden_fields, action.payload] };
            } else {
                return {
                    ...state, hidden_fields: [
                        ...state.hidden_fields.slice(0, field_index),
                        ...state.hidden_fields.slice(field_index + 1)
                    ]
                };
            }
        case SET_DATA:
            return { 
                ...state, 
                data: action.payload.data,
                fields: action.payload.fields,
            }
        case SET_STAGE:
            return { 
                ...state, 
                stage: action.payload
            }
        case SET_FILE:
            return { 
                ...state, 
                file: action.payload
            }
        case ADD_CHARITY_NUMBERS:
            return {
                ...state,
                charity_numbers: action.payload
            }
        case ADD_ORG_RECORD:
            return {
                ...state,
                org_data: {
                    ...state.org_data, 
                    [action.payload.charity_number]: action.payload.record
                }
            }
        case SET_FIELD_NAMES:
            return {
                ...state,
                charity_number_field: (action.payload.field_name == 'charity_number_field' ? action.payload.field_value : ''),
                org_id_field: (action.payload.field_name == 'org_id_field' ? action.payload.field_value : ''),
            }
        case SET_FIELDS_TO_ADD:
            return {
                ...state,
                fields_to_add: action.payload
            }
        default:
            return state;
    }
};

export default rootReducer;
