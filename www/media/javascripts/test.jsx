var Foo = React.createClass({
  render: function()
    {
    console.log('Before');
    for (var key in this.props)
      {
      console.log(key);
      }
    console.log(this.props);
    console.log('After');
    return <h2>Check log.</h2>;
    }
  });
var calculate = function()
  {
  return 10;
  }
React.render(<Foo height="10" width="10" />,
  document.getElementById('main'));
