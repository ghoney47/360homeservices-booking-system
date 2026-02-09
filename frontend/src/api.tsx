import axios from 'axios';

//creating instance of axios with base URL
const api = axios.create({
    baseURL:'http://localhost:8000'
});

//TODO: make sure to import this api to every frontend file, 

export default api;