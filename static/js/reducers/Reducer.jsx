import { MATCH_RESULT, UNMATCH_RESULT, TOGGLE_FIELD } from "../constants/action-types";

const initialState = {
    data: [],
    reconcile_field: "charity_name",
    charity_number_field: "charity_number",
    fields: [],
    reconcile_results: {},
    hidden_fields: []
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
        default:
            return state;
    }
};

export default rootReducer;
