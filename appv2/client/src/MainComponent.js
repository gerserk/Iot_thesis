import { useCallback, useState } from "react";
import axios from 'axios';
import './MainComponent.css';

const MainComponent = () => {
  const [jsonData, setJsonData] = useState(null);
  const [value, setValue] = useState('');

  const getJsonData = useCallback(async () => {
    const response = await axios.get('/api/ping');
    setJsonData(response.data);
  }, []);

  const saveJsonData = useCallback(async event => {
    event.preventDefault();

    await axios.post('/api/info_bucket', {
      value
    });

    setValue('');
    await getJsonData();
  }, [value, getJsonData]);

  return (
    <div>
      <button onClick={getJsonData}>Get JSON Data</button><br/>
      <span className="title">JSON Data</span>
      {jsonData ? (
        <div className="json">
          <pre>{JSON.stringify(jsonData, null, 2)}</pre>
        </div>
      ) : (
        <div className="no-data">No JSON data available.</div>
      )}
      <form className="form" onSubmit={saveJsonData}>
        <label>Enter the bucket</label>
        <input value={value} onChange={event => setValue(event.target.value)} />
        <button>Submit</button>
      </form>
    </div>
  );
};

export default MainComponent;