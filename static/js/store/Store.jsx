import { createStore } from "redux";
import rootReducer from "../reducers/Reducer";

const store = createStore(rootReducer);
export default store;