import { MATCH_RESULT, UNMATCH_RESULT, SHOW_FIELD, HIDE_FIELD, TOGGLE_FIELD } from "../constants/action-types";

export const match_result = (rowid, result) => ({ type: MATCH_RESULT, payload: {rowid: rowid, result: result} });
export const unmatch_result = rowid => ({ type: UNMATCH_RESULT, payload: rowid });
export const toggle_field = field => ({ type: TOGGLE_FIELD, payload: field });
