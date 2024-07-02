#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>

int is_admin = 0;
char current_user[0x100] = {0};

void setup()
{
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
}

void registerUser()
{
  char username[0x100];
  char password[0x100];
  printf("Username: ");
  fgets(username, 0x100, stdin);
  username[strchr(username, '\n') != NULL ? strchr(username, '\n') - username : 0] = '\x00';
  printf("Password: ");
  fgets(password, 0x100, stdin);
  password[strchr(password, '\n') != NULL ? strchr(password, '\n') - password : 0] = '\x00';

  char curl_command[0x400] =  {0};
  sprintf(curl_command, "curl http://messagestorage-api:3000/register -H \"Content-Type: application/json\" -s -d '{\"username\":\"%s\", \"password\":\"%s\"}'", username, password);
  FILE* curl_fd = popen(curl_command, "r");

  char response = getc(curl_fd);
  pclose(curl_fd);

  switch (response)
  {
    case '0':
      puts("Successfully registered!");
      break;
    case '1':
      puts("User already exists!");
      break;
    default:
      puts("Got invalid response!");
      break;
  }
}

// returns 1 if successful, 0 if not
int loginUser()
{
  char username[0x100];
  char password[0x100];
  puts("Please login:");
  printf("Username: ");
  fgets(username, 0x100, stdin);
  username[strchr(username, '\n') != NULL ? strchr(username, '\n') - username : 0] = '\x00';
  printf("Password: ");
  fgets(password, 0x100, stdin);
  password[strchr(password, '\n') != NULL ? strchr(password, '\n') - password : 0] = '\x00'; 
  puts("");

  char curl_command[0x400] =  {0};
  sprintf(curl_command, "curl http://messagestorage-api:3000/login -H \"Content-Type: application/json\" -s -d '{\"username\":\"%s\", \"password\":\"%s\"}'", username, password);
  FILE* curl_fd = popen(curl_command, "r");

  char response = getc(curl_fd);
  pclose(curl_fd);

  switch (response)
  {
    case '1':
      puts("Invalid credentials!");
      return 0;
      break;
    case '0':
      memcpy(current_user, username, 0x100);
      printf("Hello there ");
      printf(username);
      puts("");
      return 1;
      break;
    default:
      puts("Got invalid response!");
      return 0;
      break;
  }
}

void printMenuOne()
{
  puts("\n1) Login");
  puts("2) Register");
  puts("3) Debug");
  printf("> ");
}

void printMenuTwo()
{
  puts("\n1) Get message");
  puts("2) Store message");
  puts("3) Log out");
  puts("4) Debug");
  printf("> ");
}

void win()
{
  is_admin = 1;
}

void getMessage()
{
  char curl_command[0x400] =  {0};
  sprintf(curl_command, "curl http://messagestorage-api:3000/getmessages -H \"Content-Type: application/json\" -s -d '{\"username\":\"%s\", \"isadmin\":\"%s\"}'", current_user, is_admin ? "True" : "False");
  FILE* curl_fd = popen(curl_command, "r");

  char backend_response[0x1000] = {0};
  char* retval = NULL;

  retval = fgets(backend_response, 0x1000, curl_fd);
  if (retval == NULL)
  {
    puts("Got invalid response!");
    return;
  }
  pclose(curl_fd);

  printf("Your messages: %s\n", backend_response);
}

void readMessage(char message[48])
{
  char temp_message[48] = {0};
  printf("Give me your message: ");
  fgets(temp_message, 0x48, stdin);
  strncpy(message, temp_message, 48);
}

void setMessage()
{
  char message[48] = {0};
  readMessage(message);
  message[strchr(message, '\n') != NULL ? strchr(message, '\n') - message : 0] = '\x00';

  char curl_command[0x400] =  {0};
  sprintf(curl_command, "curl http://messagestorage-api:3000/setmessage -H \"Content-Type: application/json\" -s -d '{\"username\":\"%s\", \"message\":\"%s\"}'", current_user, message);
  FILE* curl_fd = popen(curl_command, "r");

  char response = getc(curl_fd);
  pclose(curl_fd);

  switch (response)
  {
    case '0':
      puts("Successfully saved message");
      break;
    default:
      puts("Got invalid response!");
      break;
  }
}

// prints symbols to make exploiting possible -- DO NOT TOUCH
void debug()
{
  printf("is_admin: %p\n", &is_admin);
  printf("win: %p\n", win);
  printf("getMessage: %p\n", getMessage);
}

int main(void)
{
  setup();

  int logged_in = 0;
  int choice = 0;

  puts("Welcome to our super secure message storage!");
  while (1)
  {
    choice = 0;
    while (!logged_in)
    {
      printMenuOne();
      scanf("%d", &choice);
      getchar();
      
      switch (choice)
      {
        case 1:
          logged_in = loginUser();
          break;
        case 2:
          registerUser();
          break;
        case 3:
          debug();
          break;
        default:
          exit(0);
          break;
      }
    }
    
    // logged in logic
    choice = 0;
    printMenuTwo();
    scanf("%d", &choice);
    getchar();

    switch (choice)
    {
      case 1:
        getMessage();
        break;
      case 2:
        setMessage();
        break;
      case 3:
        memset(current_user, 0x100, '\x00');
        is_admin = 0;
        logged_in = 0;
        break;
      case 4:
        debug();
        break;
      default:
        exit(0);
        break;
    }
  }
  return 0;
}