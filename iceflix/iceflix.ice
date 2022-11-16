//
// P1 version
//
[["ice-prefix"]] module IceFlix {

    ///////////// Errors /////////////
    // Raised if provided authentication token is wrong
    // Also raised if invalid user/password
    exception Unauthorized { };

    // Raised if provided media ID is not found
    exception WrongMediaId { string mediaId; };

    // Raised if some item is requested but currently unavailable
    exception TemporaryUnavailable { };

    ///////////// Custom Types /////////////
    // List of bytes
    sequence<byte> Bytes;

    // List of strings
    sequence<string> StringList;

    ///////////// File server related interfaces /////////////
    // Handle file transfer
    interface FileHandler {
        Bytes receive(int size, string userToken) throws Unauthorized;
        void close(string userToken);
    };

    // Handle administrative file upload
    interface FileUploader {
        Bytes receive(int size);
        void close();
    };

    // File service
    interface FileService {
        FileHandler* openFile(string mediaId, string userToken) throws Unauthorized;
        string uploadFile(FileUploader* uploader, string adminToken) throws Unauthorized;
        void removeFile(string mediaId, string adminToken) throws Unauthorized, WrongMediaId;
    };

    ///////////// Catalog service related structs and interfaces /////////////
    // Media info
    struct MediaInfo {
        string name;
        StringList tags;
     };

    // Media location
    struct Media {
        string mediaId;
        FileService *provider;
        MediaInfo info;
    };

    // MediaCatalog service
    interface MediaCatalog {
        Media getTile(string mediaId, string userToken) throws WrongMediaId, TemporaryUnavailable, Unauthorized;

        StringList getTilesByName(string name, bool exact);
        StringList getTilesByTags(StringList tags, bool includeAllTags, string userToken) throws Unauthorized;

        void newMedia(string mediaId);
        void removeMedia(string mediaId);
        void renameTile(string mediaId, string name, string adminToken) throws Unauthorized, WrongMediaId;

        void addTags(string mediaId, StringList tags, string userToken) throws Unauthorized, WrongMediaId;
        void removeTags(string mediaId, StringList tags, string userToken) throws Unauthorized, WrongMediaId;
    };

    ///////////// Auth server /////////////
    interface Authenticator {
        string refreshAuthorization(string user, string passwordHash) throws Unauthorized;
        bool isAuthorized(string userToken);
        string whois(string userToken) throws Unauthorized;
        bool isAdmin(string adminToken);

        void addUser(string user, string passwordHash, string adminToken) throws Unauthorized, TemporaryUnavailable;
        void removeUser(string user, string adminToken) throws Unauthorized, TemporaryUnavailable;
    };

    ///////////// Main server /////////////
    interface Main {
        Authenticator* getAuthenticator() throws TemporaryUnavailable;
        MediaCatalog* getCatalog() throws TemporaryUnavailable;

        void newService(Object* service, string serviceId);
        void announce(Object* service, string serviceId);
    };
};
