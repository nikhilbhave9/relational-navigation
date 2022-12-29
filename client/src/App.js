import { useState } from 'react';
import axios from 'axios';

import './App.css';
import Container from 'react-bootstrap/Container';
import Navbar from 'react-bootstrap/Navbar';
import Row from 'react-bootstrap/Row';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';



function App() {

  const [instructions, setInstructions] = useState([]); // Get instructions as a list of strings
  const [count, setCount] = useState(0); // Count to keep track of current instruction
  const [currentInstruction, setCurrentInstruction] = useState('');
  const [source, setSource] = useState([]); // Get source as a string
  const [destination, setDestination] = useState([]); // Get destination as a string

  const handleSourceChange = (event) => {
    event.preventDefault(); // prevent the default action
    setSource(event.target.value);

  }

  const handleDestinationChange = (event) => {
    event.preventDefault(); // prevent the default action
    setDestination(event.target.value);
  }

  const handleSubmit = (event) => {
    event.preventDefault();
    axios.get('/instructions', {
      params: {
        key1: source,
        key2: destination
      },
    })
      .then(response => {
        // console.log(response.data);
        setInstructions(response.data);
        setCurrentInstruction(instructions[count]);
      })
      .catch(error => {
        console.log(error);
      });

  }

  const handleClick = () => {
    setCurrentInstruction(instructions[count]);
    setCount(count + 1);
  }

  // useEffect(() => {
  //   axios.get('/instructions')
  //     .then((response) => {
  //       console.log(response.data);
  //       setInstructions(response.data);
  //     })
  //     .catch((error) => {
  //       console.log(error);
  //     });
  // }, []);
  
  // comment

  return (
    <>
      <Navbar bg='light'>
        <Container>
          <Navbar.Brand href="/">
            <img
              alt=""
              src="https://png.pngtree.com/png-vector/20190129/ourlarge/pngtree-navigation-vector-icon-png-image_355944.jpg"
              width="30"
              height="30"
              className="d-inline-block align-top"
            />{' '}
            NavApp
          </Navbar.Brand>
        </Container>
      </Navbar>

      <Container style={{ textAlign: 'center' }}>
        <Row className='m-5'>
          <h1>Ashoka Relational Navigation</h1>
        </Row>



        <Container >
          {/* style={{ width: '60%' }} */}

          <Row className='m-2 pt-2'>
            <Col>
              {/* <div className='mb-4'>
                <h3>Enter navigation parameters</h3>
              </div> */}
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3" controlId="formBasicEmail">
                  <Form.Label>Where are you?</Form.Label>
                  <Form.Control type="text" placeholder="Source" onChange={handleSourceChange} />
                </Form.Group>

                <Form.Group className="mb-3" controlId="formBasicPassword">
                  <Form.Label>Where do you want to go?</Form.Label>
                  <Form.Control type="text" placeholder="Destination" onChange={handleDestinationChange} />
                </Form.Group>

                <Button variant="primary" type="submit" >
                  Submit
                </Button>
              </Form>
            </Col>

            <Col>
              <div className='mb-4'>
                <h3>Navigation</h3>
              </div>
              <Card >

                <Card.Body>
                  <Card.Title>Current Instruction</Card.Title>
                  <Card.Text>
                    {currentInstruction}
                  </Card.Text>
                  <Button variant="primary" onClick={handleClick}>Next</Button>
                </Card.Body>
              </Card>
            </Col>


          </Row>




        </Container>

      </Container>
    </>
  );
}

export default App;
