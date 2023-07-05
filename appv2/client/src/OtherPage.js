import { Link } from 'react-router-dom';

const OtherPage = () => {
return(
    <div>
        I'm on another page!
        <Link to ="/">Go back to home screen</Link>
    </div>
    );

};

export default OtherPage;