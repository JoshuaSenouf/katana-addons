#include <FnAttribute/FnAttribute.h>
#include <FnAttribute/FnDataBuilder.h>
#include <FnAttribute/FnGroupBuilder.h>
#include <FnGeolib/op/FnGeolibOp.h>
#include <FnGeolib/util/Path.h>
#include <FnGeolibServices/FnGeolibCookInterfaceUtilsService.h>
#include <FnGeolibServices/FnResolutionTable.h>
#include <FnGeolibServices/FnXFormUtil.h>
#include <FnPluginSystem/FnPlugin.h>


namespace {

class PassCollections : public Foundry::Katana::GeolibOp
{
	public:
		static void setup(Foundry::Katana::GeolibSetupInterface& interface);
		static void cook(Foundry::Katana::GeolibCookInterface& interface);
	private:
		static void setPassCollections(Foundry::Katana::GeolibCookInterface& interface,
    		const std::string& activePassLocation);
		static void setDlPassCollections(Foundry::Katana::GeolibCookInterface& interface,
    		const std::string& activePassLocation,
            const std::vector<std::string>& passLocationSplitVec);
		static void setPRManPassCollections(Foundry::Katana::GeolibCookInterface& interface,
    		const std::string& activePassLocation,
            const std::vector<std::string>& passLocationSplitVec);
		static void setArnoldPassCollections(Foundry::Katana::GeolibCookInterface& interface,
    		const std::string& activePassLocation,
			const std::vector<std::string>& passLocationSplitVec);
		static bool isCurrentRenderer(Foundry::Katana::GeolibCookInterface& interface,
			const std::string& rendererToTest);
		static const std::string getEnvVar(const std::string& envVarName,
			const std::string& defaultValue = "");
		static const std::vector<std::string> splitString(const std::string& stringToSplit,
			const std::string& delimChars = "",
			int numSplit = -1);
};


DEFINE_GEOLIBOP_PLUGIN(PassCollections)

} // Katana anonymous namespace.

void registerPlugins()
{
    REGISTER_PLUGIN(PassCollections, "PassCollections", 0, 1);
}