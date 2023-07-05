import { useCallback, useState } from "react";
import axios from 'axios';
import './MainComponent.css';

const MainComponent = () =>{
    const [values, setValues] = useState([]);
    const [value, setValue] = useState('');

    const getAllNumbers = useCallback(async()=> {
        // use nginx to rendirect to right URLs (don't have /api in original app)
        const values = await axios.get('/api/info_all_buckets');
        setValues(values)
        
    },[]);

    const saveNumber = useCallback(
        async event => {
        event.preventDefault();

        await axios.post('/api/info_bucket',{
            value
        })

        setValue('');
        await getAllNumbers();

    },[value, getAllNumbers]);


    return(
        <div>
            <button onClick={getAllNumbers}>Get all values </button><br/>
            <span className= "title"> Values</span>
            <div className="values">
                {values.map((value) => <div className="value">{value} </div>)}
            </div>
            <form className="form" onSubmit={saveNumber}>
                <label> Enter the bucket</label>
                <input value={value} onChange={((event)=> {setValue(event.target.value)})} />
                <button>Submit</button>
            </form>
        </div>
    );
};

export default MainComponent;