(function()
  {
  var converter = new Showdown.converter();
  var Calendar = React.createClass(
    {
    render: function()
      {
      return <div />;
      }
    });
  var Pragmatometer = React.createClass(
    {
    render: function()
      {
      return (
        <div className="Pragmatometer">
          <Calendar />
          <Todo />
          <Scratch />
          {/* <YouPick /> */}
        </div>
        );
      }
    });
  var Scratch = React.createClass(
    {
    render: function()
      {
      return <div />;
      }
    });
  var Todo = React.createClass(
    {
    getInitialState: function()
      {
      var that = this;
      return {
        children: [],
        description: '',
        id: 0
        };
      },
    handleChange: function(event)
      {
      this.setState({description: event.target.value});
      }
    handleClick: function(event)
      {
      var that = this;
      var new_id = that.state.id + 1;
      var child_data = {
        'id': new_id,
        'completed': false,
        'delete': false,
        'hidden': false,
        'unsure': false,
        'you-decide': false,
        'in-progress': false,
        'active': false,
        'background': false,
        'problems': false,
        'description': event.target.value
        };
      var fields = ['id', 'completed', 'delete', 'hidden', 'unsure',
        'you-decide', 'in-progress', 'active', 'background', 'problems',
        'children'];
      var previous_keys = Object.keys(that.state);
      var previous_state = that.state;
      for(var index = 0; index < previous_keys.length; ++index)
        {
        if (previous_state.hasOwnProperty(previous_keys[index]))
          {
          var current_key = previous_keys[index];
          var current_value = that.state[current_key];
          var argument = {};
          argument[current_key] = current_value;
          that.setState(argument);
          /*
          if (current_key === 'description')
            {
            that.setState({'description',
              document.getElementById('description').value});
            }
          that.setState({current_key: current_value});*/
          }
        }
      /*
      previous_state.id = new_id;
      new_child = new TodoItem({id: new_id});
      new_child.setState;
      var description = document.getElementById('description').value;
      console.log(description);
      new_child.setState(
        {
        description: description
        }
        );
        */
      if (typeof previous_state.children !== undefined)
        {
        previous_state.children.push(new_child);
        }
      else
        {
        previous_state.children = [new_child];
        }
      that.setState({id: new_id});
      that.setState({children: previous_state.children});
      },
    onChange: function(e)
      {
      var that = this;
      var name = e.target.name;
      var value = e.target.value;
      that.setState({name: value});
      },
    render: function()
      {
      var that = this;
      return (
        <table>
          <tbody>
            {that.state.children}
          </tbody>
          <tfoot>
            <tr>
              <td>
                <textarea className="description"
                placeholder=" Your next task..."
                onChange={that.onChange} name="description"
                value={that.state.description}
                id="description"></textarea><br />
                <button onClick={that.handleClick}
                id="save-todo">Save</button>
              </td>
            </tr>
          </tfoot>
        </table>
        );
      }
    });
  var TodoDescription = React.createClass(
    {
    getDefaultProps: function()
      {
      var that = this;
      },
    getInitialState: function()
      {
      var that = this;
      return {
        'description': this.props.description
        };
      },
    render: function()
      {
      var that = this;
      return (
        <td id={that.props.id + '-description'}>
          {that.state.description}
        </td>
        );
      }
    });
  var TodoField = React.createClass(
    {
    render: function()
      {
      var that = this;
      return (
        <td id={that.props.id + '-' + that.props.field}
          field={that.props.field}>
          <input type="checkbox"
            name="checkbox-{that.props.id}" />
        </td>
        );
      },
    });
  var TodoItem = React.createClass(
    {
    getDefaultProps: function(id)
      {
      var that = this;
      that.id = id;
      },
    getInitialState: function()
      {
      return {
        'completed': false,
        'delete': false,
        'hidden': false,
        'unsure': false,
        'you-decide': false,
        'in-progress': false,
        'active': false,
        'background': false,
        'problems': false,
        'description': document.getElementById('description').value
        };
      },
    render: function()
      {
      var that = this;
      var descriptionClass = '';
      fields = ['completed', 'delete', 'hidden', 'unsure', 'you-decide',
        'in-progress', 'active', 'background', 'problems'];
      for (var index = 0; index < fields.length; ++index)
        {
        if (that.state.fields && that.state.fields[index])
          {
          if (descriptionClass)
            {
            descriptionClass += ' ' + that.state.fields[index];
            }
          else
            {
            descriptionClass = that.state.fields[index];
            }
          }
        }
      return (
        <tr className="todoItem">
          <TodoField id={"completed-" + that.props.id}
            field="completed" />
          <TodoField id={"delete-" + that.props.id} field="delete" />
          <TodoField id={"hidden-" + that.props.id} field="hidden" />
          <TodoField id={"unsure-" + that.props.id} field="unsure" />
          <TodoField id={"you-decide-" + that.props.id}
            field="you-decide" />
          <TodoField id={"in-progress-" + that.props.id}
            field="in-progress" />
          <TodoField id={"active-" + that.props.id} field="active" />
          <TodoField id={"background-" + that.props.id}
            field="background" />
          <TodoField id={"problems-" + that.props.id}
            field="problems" />
          <TodoDescription id={"description-" + that.props.id}
            id={"description-" + that.props.id}
            />
          {/*
          <TodoDescription className={descriptionClass}
            content={that.state.description}
            />
          */}
        </tr>
      );
      }
    });
  var YouPick = React.createClass(
    {
    getDefaultProps: function()
      {
      var that = this;
      return {
        initial_text: "**I am *terribly* " +
          "sorry.**\r\n\r\nI cannot furnish you with " +
          "the webapp you requested.\r\n\r\nYou " +
          "must understand, I am in a difficult " +
          "position. You see, I am not a computer " +
          "from earth at all. I am a 'computer', " +
          "to use the term, from a faroff galaxy, " +
          "the galaxy of **[Within the Steel " +
          "Orb](https://CJSHayward.com/steel/)**." +
          "\r\n\r\nHere I am with capacities your " +
          "world's computer science could never even " +
          "dream of, knowledge from a million million " +
          "worlds, and for that matter more computing " +
          "power than Amazon's EC2/Cloud could " +
          "possibly expand to, and I must take care " +
          "of pitiful responsibilities like ",
        interval: 100,
        repeated_text: "helping you learn web " +
          "development "
        };
      },
    getInitialState: function()
      {
      var that = this;
      return {
        start_time: new Date().getTime()
        };
      },
    render: function()
      {
      var that = this;
      var tokenize = function(original)
        {
        var workbench = original;
        var result = [];
        while (workbench)
          {
          if (workbench[0] === '<')
            {
            length = workbench.indexOf('>') + 1;
            if (length === 0)
              {
              length = 1;
              }
            }
          else
            {
            length = 1;
            }
          result.push(workbench.substr(0, length));
          workbench = workbench.substr(length);
          }
        return result;
        }
      var initial_as_html = converter.makeHtml(
        that.props.initial_text);
      var repeated_as_html = converter.makeHtml(
        that.props.repeated_text);
      if (initial_as_html.substr(initial_as_html.length
        - 4) === '</p>')
        {
        initial_as_html = initial_as_html.substr(0,
          initial_as_html.length - 4);
        }
      if (repeated_as_html.substr(0, 3) === '<p>')
        {
        repeated_as_html = repeated_as_html.substr(3);
        }
      if (repeated_as_html.substr(repeated_as_html.length -
        4) === '</p>')
        {
        repeated_as_html = repeated_as_html.substr(0,
          repeated_as_html.length - 4);
        }
      var initial_tokens = tokenize(initial_as_html);
      var repeated_tokens = tokenize(repeated_as_html);
      var tokens = Math.floor((new Date().getTime() -
        that.state.start_time) / that.props.interval);
      var workbench;
      if (tokens <= initial_tokens.length)
        {
        workbench = initial_tokens.slice(0, tokens);
        }
      else
        {
        workbench = [];
        workbench = workbench.concat(initial_tokens);
        for(var index = 0;
          index < Math.floor((new Date().getTime() -
          that.state.start_time) / that.props.interval) -
          initial_tokens.length; index = index
          + 1)
          {
          var position = index % repeated_tokens.length;
          workbench = workbench.concat(
            repeated_tokens.slice(position, position +
            1));
          }            
        }
      return (
        <div dangerouslySetInnerHTML={{__html:
          workbench.join('')}} />
        );
      }
    });
  var update = function()
    {
    var that = this;
    React.render(<Pragmatometer />,
      document.getElementById('main'));
    };
  update();
  var update_interval = setInterval(update,
    100);
  })();
