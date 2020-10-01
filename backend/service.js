import axios from 'axios';

const apiUrl = "http://127.0.0.1:5000"

async function audioExecute(containerFile, containerFileName, inputFile, inputFileName, key, encrypted, randomized, audioType) {
    let formData = new FormData();
    console.log(containerFileName);
    formData.append('containerFile', containerFile, containerFileName);
    formData.append('inputFile', inputFile, inputFileName);
    formData.append('key', key);
    formData.append('encrypted', encrypted);
    formData.append('randomized', randomized);
    formData.append('audioType', audioType);

    return await axios.post(`${apiUrl}/audio/embedding`, formData,
        {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        }
    ).then(result => {
        console.log("Request Came");
        return result;
    }).catch(error => {
        console.log("Error");
        if (error.response.status === 500){
            alert(error.response.data);
        }
    });
}

const service = {
    audioExecute
};

export default service;
