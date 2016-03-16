var Foo = React.createClass({displayName: "Foo",
  render: function()
    {
    return React.createElement("h2", null, "Check log.");
    console.log('Before');
    for (var key in this.props)
      {
      console.log(key);
      }
    console.log(this.props);
    console.log('After');
    }
  });
var calculate = function()
  {
  return 10;
  }
React.render(React.createElement(Foo, {height: "10", width: calculate}),
  document.getElementById('main'));
